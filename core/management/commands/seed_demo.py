from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from products.models import Category, Product
from accounts.models import UserRole


class Command(BaseCommand):
    help = "Seed demo data (products + roles)."

    def handle(self, *args, **options):
        cat, _ = Category.objects.get_or_create(name="Skincare", slug="skincare")
        demo_products = [
            ("Hydrating Eye Serum", 56.00, 20),
            ("Foaming Facial Cleanser", 85.00, 15),
            ("Daily Moisturiser", 49.00, 30),
            ("Gentle Toner", 32.00, 25),
            ("Vitamin C Serum", 65.00, 12),
            ("Night Repair Cream", 72.00, 10),
        ]
        for name, price, stock in demo_products:
            Product.objects.get_or_create(
                name=name,
                slug=slugify(name),
                defaults={
                    "category": cat,
                    "price": price,
                    "stock": stock,
                    "description": "Premium skincare product.",
                },
            )

        User = get_user_model()
        admin_user, _ = User.objects.get_or_create(
            username="admin", defaults={"email": "admin@example.com"}
        )
        admin_user.set_password("admin12345")
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        analyst, _ = User.objects.get_or_create(
            username="analyst", defaults={"email": "analyst@example.com"}
        )
        analyst.set_password("analyst12345")
        analyst.is_staff = True
        analyst.save()
        UserRole.objects.get_or_create(user=analyst, defaults={"role": "analyst"})

        ops, _ = User.objects.get_or_create(
            username="ops", defaults={"email": "ops@example.com"}
        )
        ops.set_password("ops12345")
        ops.is_staff = True
        ops.save()
        UserRole.objects.get_or_create(user=ops, defaults={"role": "ops"})

        self.stdout.write(
            self.style.SUCCESS(
                "Seed complete. Users: admin/admin12345, analyst/analyst12345, ops/ops12345"
            )
        )
