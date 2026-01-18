from django.urls import path
from .views import cart_view, cart_add, cart_update, cart_remove, cart_clear

urlpatterns = [
    path("", cart_view, name="cart"),
    path("add/", cart_add, name="cart-add"),
    path("update/", cart_update, name="cart-update"),
    path("remove/", cart_remove, name="cart-remove"),
    path("clear/", cart_clear, name="cart-clear"),
]
