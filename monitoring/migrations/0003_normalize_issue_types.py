from django.db import migrations


def normalize_issue_types(apps, schema_editor):
    DataQualityIssue = apps.get_model("monitoring", "DataQualityIssue")
    DataQualityIssue.objects.filter(issue_type="order_state").update(
        issue_type="invalid_order_state"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("monitoring", "0002_alter_dataqualityissue_options_and_more"),
    ]

    operations = [
        migrations.RunPython(normalize_issue_types, migrations.RunPython.noop),
    ]
