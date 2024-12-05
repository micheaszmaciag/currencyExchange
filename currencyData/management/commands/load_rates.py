from django.core.management.base import BaseCommand
from currencyData.models import Currency
from currencyData.services import get_currency

class Command(BaseCommand):
    help = 'FETCH DATA FROM NBP API ADD TO THE MODEL'

    def handle(self, *args, **options):
        # Delete all existing objects
        if Currency.objects.exists():
            Currency.objects.all().delete()

        # Fetch and add new currencies
        for code, rate in get_currency().items():
            Currency.objects.get_or_create(code=code, rate_currency=rate)
        Currency.objects.get_or_create(code='PLN', rate_currency=1)


