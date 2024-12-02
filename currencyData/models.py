from django.db import models
from django.core.validators import MinValueValidator
import uuid
import requests


# Create your models here.

class Currency(models.Model):
    code = models.CharField(max_length=3, null=True, blank=True)
    rate_currency = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    id = models.UUIDField(default=uuid.uuid4, unique=True,
                          primary_key=True, editable=False)

    def __str__(self):
        return f'{self.code}'


class CurrencyBidNow(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='base_currency_bids')
    currency_to_buy = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='expected_currency')
    name_of_transaction = models.CharField(max_length=10, null=True, blank=True)
    exchange_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)] ,null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True,
                          primary_key=True, editable=False)

    def __str__(self):
        return f"{self.name_of_transaction}"

    def save(self, *args, force_insert=False, force_update=False, using=None, update_fields=None, **kwargs):
        if self.currency and self.currency_to_buy:
            if self.currency.rate_currency > 0 and self.currency_to_buy.rate_currency > 0:
                self.exchange_rate = round(self.currency.rate_currency / self.currency_to_buy.rate_currency, 3)

        if self.currency.code and self.currency_to_buy.code :
            self.name_of_transaction = self.currency.code + self.currency_to_buy.code
        super().save(*args, **kwargs)
    class Meta:
        ordering = ['-date']

class CurrencyHistoryBid(models.Model):
    history_transaction_name = models.CharField(max_length=10, null= True, blank=True)
    history_transaction_rate = models.FloatField(default=0.0,null= True, blank=True)
    history_date = models.DateTimeField(auto_now_add=False)
    id = models.UUIDField(default=uuid.uuid4, unique=True,
                          primary_key=True, editable=False)

    def __str__(self):
        return f'{self.history_transaction_name}'

    class Meta:
        ordering = ['-history_date']