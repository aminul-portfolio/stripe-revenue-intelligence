from django.urls import path
from .views import issues

urlpatterns = [path("issues/", issues, name="monitoring-issues")]
