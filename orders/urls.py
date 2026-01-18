from django.urls import path
from . import views

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("<int:order_id>/", views.order_detail, name="order-detail"),
    # Ops/Admin lifecycle actions (POST-only)
    path("<int:order_id>/cancel/", views.order_cancel, name="order-cancel"),
    path("<int:order_id>/fulfill/", views.order_fulfill, name="order-fulfill"),
]
