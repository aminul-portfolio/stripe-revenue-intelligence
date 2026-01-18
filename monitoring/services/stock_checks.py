from products.models import Product, ProductVariant
from monitoring.models import DataQualityIssue


def check_stock_anomalies():
    # Product negative stock
    for p in Product.objects.filter(stock__lt=0):
        DataQualityIssue.objects.get_or_create(
            issue_type="stock_anomaly",
            reference_id=f"product:{p.id}",
            defaults={
                "description": f"Negative product stock: {p.name} (stock={p.stock})"
            },
        )

    # Variant negative stock
    for v in ProductVariant.objects.filter(stock__lt=0):
        DataQualityIssue.objects.get_or_create(
            issue_type="stock_anomaly",
            reference_id=f"variant:{v.id}",
            defaults={
                "description": f"Negative variant stock: {v.sku} (variant_id={v.id}, stock={v.stock})"
            },
        )
