from django.urls import path

from .views import product_list_api, register_order, register_order_detail

app_name = "foodcartapp"

urlpatterns = [
    path('products/', product_list_api),
    path('order/', register_order),
    path('order/<int:pk>/', register_order_detail)
]
