import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order, OrderItem
from .serializers import OrderSerializer


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['GET', 'POST'])
def register_order_api(request):
    if request.method == 'GET':
        order = Order.objects.all()
        serializer_order = OrderSerializer(order, many=True)
        return Response(serializer_order.data)

    elif request.method == 'POST':
        order = request.data
        customer, created = Order.objects.get_or_create(
            firstname=order['firstname'], lastname=order['lastname'], phonenumber=order['phonenumber'],
            address=order['address'])

        for product in order['products']:
            OrderItem.objects.create(order=customer,
                                     product=Product.objects.get(id=product['product']), quantity=product['quantity'])
        serializer = OrderSerializer(instance=customer)
        #if serializer.is_valid():
            #serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)