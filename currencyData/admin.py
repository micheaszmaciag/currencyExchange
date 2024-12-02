from django.contrib import admin
from .models import Currency, CurrencyBidNow, CurrencyHistoryBid
# Register your models here.


admin.site.register(Currency)
admin.site.register(CurrencyBidNow)
admin.site.register(CurrencyHistoryBid)