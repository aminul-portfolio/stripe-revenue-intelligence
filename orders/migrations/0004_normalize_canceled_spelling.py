from django.db import migrations


def forwards(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    Order.objects.filter(status="cancelled").update(status="canceled")


def backwards(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    Order.objects.filter(status="canceled").update(status="cancelled")


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0003_alter_order_options_order_refund_amount_pennies_and_more"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
