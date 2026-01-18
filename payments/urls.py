from django.urls import path
from . import views

urlpatterns = [
    path("start/<int:order_id>/", views.start_payment, name="start-payment"),
    path("webhook/", views.stripe_webhook, name="stripe-webhook"),
]
