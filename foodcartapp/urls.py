from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers

from .views import product_list_api, banners_list_api, register_order

app_name = "foodcartapp"

urlpatterns = [
    path('products/', product_list_api),
    path('banners/', banners_list_api),
    path('order/', register_order)
]
