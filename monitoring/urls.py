from django.urls import path
from .views import issues, healthz

app_name = "monitoring"

urlpatterns = [
    path("issues/", issues, name="monitoring-issues"),
    path("healthz/", healthz, name="healthz"),
]
