from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CurrencyBidNow, CurrencyHistoryBid


def createTransaction(sender, instance, created, **kwargs):
    if created:
        currency_bid_now = instance
        history_bid = CurrencyHistoryBid.objects.create(
            history_transaction_name=currency_bid_now.name_of_transaction,
            history_transaction_rate=currency_bid_now.exchange_rate,
            history_date=currency_bid_now.date
        )







post_save.connect(createTransaction, sender=CurrencyBidNow)

