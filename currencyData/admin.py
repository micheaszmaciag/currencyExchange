from django.utils import timezone
from django.contrib import admin
from rangefilter.filters import DateRangeFilter
from .services import fetch_historical_rate
from .models import CurrencyHistoryBid, Currency
from django.core.cache import cache

# Register your models here.



@admin.register(CurrencyHistoryBid)
class CurrencyHistoryBidAdmin(admin.ModelAdmin):
    list_display = ['transaction_name', 'history_date', 'history_transaction_rate']
    list_filter = [('history_date', DateRangeFilter), 'transaction_name']


    def changelist_view(self, request, extra_context=None):
        # Using the cache mechanism to avoid unnecessary calls to the fetch_historical_rate
        last_update = cache.get('last_historical_update')
        if not last_update:
            fetch_historical_rate()
            cache.set('last_historical_update', timezone.now())
        return super().changelist_view(request, extra_context=extra_context)



