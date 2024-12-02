from django.apps import AppConfig


class CurrencydataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'currencyData'


    def ready(self):
        import currencyData.signals
        from .models import Currency
        from .services import get_currency

        for code, rate in get_currency().items():
            Currency.objects.get_or_create(code=code, rate_currency=rate)
        Currency.objects.get_or_create(code='PLN', rate_currency= 1)
