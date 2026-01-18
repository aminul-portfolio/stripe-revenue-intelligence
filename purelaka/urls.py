from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("account/", include("accounts.urls")),
    path("products/", include("products.urls")),
    path("cart/", include("cart.urls")),
    path("orders/", include("orders.urls")),
    path("payments/", include("payments.urls")),
    path("subscriptions/", include("subscriptions.urls")),
    path("wishlist/", include("wishlist.urls")),
    path("analytics/", include("analyticsapp.urls")),
    path("monitoring/", include("monitoring.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
