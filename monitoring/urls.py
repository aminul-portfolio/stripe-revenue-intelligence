from django.urls import path
from .views import issues

app_name = "monitoring"

urlpatterns = [path("issues/", issues, name="monitoring-issues")]
