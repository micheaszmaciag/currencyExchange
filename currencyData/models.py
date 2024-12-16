from django.db import models
from django.core.validators import MinValueValidator
import uuid


class Currency(models.Model):
    code = models.CharField(
        max_length=3,
        null=True,
        blank=True
    )

    rate_currency = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)]
    )

    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False
    )

    def __str__(self):
        return f'{self.code}'



class CurrencyExchangeRate(models.Model):
    class Meta:
        ordering = ['currency_exchange_pair', '-currency_exchange_date']
        indexes=[
            models.Index(fields=['currency_exchange_pair']),
            models.Index(fields=['currency_exchange_date'])
        ]

    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    currency_exchange_pair = models.CharField(
        max_length=10,
        null=True,
        blank=True
    )
    currency_exchange_rate = models.FloatField(
        default=0.0,
        null=True,
        blank=True
    )
    currency_exchange_date = models.DateField(
        auto_now_add=False,
        null=True,
        blank=True
    )
    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False
    )

    def __str__(self):
        return f'{self.currency_exchange_pair} - {self.currency_exchange_date}'

