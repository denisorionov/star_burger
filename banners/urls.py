from django.urls import path

from .views import banners_list_api

app_name = "banners"

urlpatterns = [
    path('banners/', banners_list_api)
    ]
