from django.urls import path, include
from django.views.generic import RedirectView

from .views import home, healthz

urlpatterns = [
    path("", home, name="home"),
    path("healthz/", healthz, name="healthz"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/profile/", RedirectView.as_view(url="/account/", permanent=False)),
]
