from django.contrib import admin
from django.urls import path
from rangefilter.filters import DateRangeFilter
from .models import CurrencyExchangeRate
from django.http import HttpResponse
from .services import generate_excel_currencies



@admin.register(CurrencyExchangeRate)
class CurrencyExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['currency_exchange_pair', 'currency_exchange_rate', 'currency_exchange_date']
    list_filter = [('currency_exchange_date', DateRangeFilter), 'currency_exchange_pair']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-filtered/', self.admin_site.admin_view(self.export_currencies_pair),
                 name='export_filtered_currencies'),
        ]
        return custom_urls + urls

    def export_currencies_pair(self, request):
        pair = request.GET.get('currency_exchange_pair')

        if not pair:
            return HttpResponse("If you want to Export history to Excel first you have to choose <b>currency pair</b> by clicking for example <b>EURUSD</b> in FILTER"
                                " <a href='/admin/currencyData/currencyexchangerate/'>Go back</a>", content_type="text/html")

        queryset = CurrencyExchangeRate.objects.filter(currency_exchange_pair=pair)

        if not queryset.exists():
            return HttpResponse(f"There is no pair of currencies like: {pair} <a href='/admin/currencyData/currencyexchangerate/'>GO BACK</a>")


        return generate_excel_currencies(queryset,pair)


