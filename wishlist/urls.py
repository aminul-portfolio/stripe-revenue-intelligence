from django.urls import path
from .views import my_wishlist, toggle

urlpatterns = [
    path("", my_wishlist, name="my-wishlist"),
    path("toggle/<int:product_id>/", toggle, name="wishlist-toggle"),
]
