from django.core.management.base import BaseCommand
from monitoring.services.run_all import run_all_checks


class Command(BaseCommand):
    help = "Run data quality checks (payments/orders/stock)."

    def handle(self, *args, **options):
        run_all_checks()
        self.stdout.write(self.style.SUCCESS("Data quality checks executed."))
