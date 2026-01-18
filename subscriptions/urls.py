from django.urls import path
from .views import (
    my_subscriptions,
    create_subscription,
    cancel,
    reactivate,
    add_payment_method,
    add_payment_method_complete,
)

urlpatterns = [
    path("", my_subscriptions, name="my-subscriptions"),
    path("create/", create_subscription, name="subscriptions-create"),
    path("payment-method/add/", add_payment_method, name="subscriptions-add-pm"),
    path(
        "payment-method/complete/",
        add_payment_method_complete,
        name="subscriptions-add-pm-complete",
    ),
    path("<int:sub_id>/cancel/", cancel, name="subscriptions-cancel"),
    path("<int:sub_id>/reactivate/", reactivate, name="subscriptions-reactivate"),
]
