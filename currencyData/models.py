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


class CurrencyHistoryBid(models.Model):
    history_transaction_name = models.CharField(max_length=10, null=True, blank=True)
    history_transaction_rate = models.FloatField(default=0.0, null=True, blank=True)
    history_date = models.DateField(auto_now_add=False)
    id = models.UUIDField(default=uuid.uuid4, unique=True,
                          primary_key=True, editable=False)

    def __str__(self):
        return f'{self.history_transaction_name} - {self.history_date.strftime("%Y-%m-%d")}'

    class Meta:
        ordering = ['history_transaction_name', '-history_date']
