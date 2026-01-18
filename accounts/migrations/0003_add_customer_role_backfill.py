from django.conf import settings
from django.db import migrations


def backfill_user_roles(apps, schema_editor):
    UserRole = apps.get_model("accounts", "UserRole")

    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(app_label, model_name)

    for u in User.objects.all():
        if UserRole.objects.filter(user_id=u.id).exists():
            continue

        if getattr(u, "is_superuser", False):
            role = "admin"
        elif getattr(u, "is_staff", False):
            role = "ops"
        else:
            role = "customer"

        UserRole.objects.create(user_id=u.id, role=role)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_alter_userrole_role"),
    ]

    operations = [
        migrations.RunPython(backfill_user_roles, migrations.RunPython.noop),
    ]
