from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="analytics-dashboard"),
    path(
        "export/kpi-summary/",
        views.export_kpi_summary_csv,
        name="analytics-export-kpi-summary",
    ),
    path("export/orders/", views.export_orders_csv, name="analytics-export-orders"),
    path(
        "export/products/", views.export_products_csv, name="analytics-export-products"
    ),
    path(
        "export/customers/",
        views.export_customers_csv,
        name="analytics-export-customers",
    ),
]
