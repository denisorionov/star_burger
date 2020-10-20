from django import forms
from django.db.models import Sum, F, DecimalField
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.views.decorators.cache import cache_page
from geopy import distance

from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem, OrderItem
from restaurateur.utils import fetch_coordinates


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:
        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@cache_page(600, cache='default', key_prefix='')
@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    apikey = '79533e90-33d0-4074-ac4c-67969fb49f88'
    order_restaurants = {}
    next_restaurant = {}
    restaurants = []

    order_items = Order.objects.annotate(
        cost=Sum(F('products__price') * F('products__quantity'),
                 output_field=DecimalField(max_digits=9, decimal_places=2)))

    for order in Order.objects.all():
        for item in order.products.all():
            for item_restaurant in RestaurantMenuItem.objects.filter(availability=True, product=item.product):
                restaurants.append(item_restaurant.restaurant.name)

        restaurants = list(
            filter(lambda restaurant: restaurants.count(restaurant) >= len(order.products.all()), restaurants))
        order_coords = fetch_coordinates(apikey, order.address)

        for restaurant in list(set(restaurants)):
            restaurant_coords = fetch_coordinates(apikey, Restaurant.objects.get(name=restaurant).address)
            next_restaurant[restaurant] = round(distance.distance(order_coords, restaurant_coords).km, 2)

        order_restaurants[order.id] = sorted(next_restaurant.items(), key=lambda x: x[1])
        restaurants = []
        next_restaurant = {}

    return render(request, template_name='order_items.html',
                  context={'order_items': order_items, 'order_restaurants': order_restaurants})
