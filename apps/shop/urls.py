from django.urls import path

from . import views
from .views import ShopView

app_name = "shop"

urlpatterns = [
    path("", ShopView.as_view(), name="browse"),
    path("cart/add/<int:pk>/", views.cart_add, name="cart_add"),
    path("quickview/<int:pk>/", views.quick_view, name="quickview"),
]
