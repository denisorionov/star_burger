from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.db.models import Sum, F, DecimalField
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from geopy import distance

from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem, OrderItem


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


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    order_restaurants = {}
    close_restaurants = {}
    restaurants = []

    order_items = Order.objects.annotate(
        cost=Sum(F('products__price') * F('products__quantity'),
                 output_field=DecimalField(max_digits=9, decimal_places=2)))

    for order in order_items:
        order_product_all = OrderItem.objects.select_related("product").filter(order=order)

        for item in order_product_all:
            product_restaurant = RestaurantMenuItem.objects.select_related("restaurant").filter(availability=True,
                                                                                                product=item.product)
            restaurants += [item_restaurant.restaurant.name for item_restaurant in product_restaurant]

        restaurants = list(
            filter(lambda restaurant: restaurants.count(restaurant) >= order_product_all.count(), restaurants))

        order_coords = cache.get(order.address)

        for restaurant in list(set(restaurants)):
            restaurant_coords = cache.get(restaurant)
            close_restaurants[restaurant] = round(distance.distance(order_coords, restaurant_coords).km, 2)

        order_restaurants[order.id] = sorted(close_restaurants.items(), key=lambda x: x[1])
        restaurants = []
        close_restaurants = {}

    return render(request, template_name='order_items.html',
                  context={'order_items': order_items, 'order_restaurants': order_restaurants})
