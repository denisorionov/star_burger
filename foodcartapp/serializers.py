from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from foodcartapp.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'products', 'firstname', 'lastname', 'phonenumber', 'address']

    def create(self, validated_data):
        return Order.objects.create(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phonenumber=validated_data['phonenumber'],
            address=validated_data['address'],
            products=validated_data['products']
        )

    def validate_products(self, value):
        if not value:
            raise ValidationError("Это поле не может быть пустым.")
        return value
