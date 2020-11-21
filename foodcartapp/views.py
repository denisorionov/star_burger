from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order
from .serializers import OrderSerializer


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
def register_order(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            orders = Order.objects.all()
            serializer_orders = OrderSerializer(orders, many=True)
            return Response(serializer_orders.data)
        return redirect("/manager/login/")

    elif request.method == 'POST':
        serializer = OrderSerializer(data=request.data)

        if serializer.is_valid():
            Order.objects.create(
                firstname=serializer.validated_data['firstname'],
                lastname=serializer.validated_data['lastname'],
                phonenumber=serializer.validated_data['phonenumber'],
                address=serializer.validated_data['address'],
                products=serializer.validated_data['products']
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
