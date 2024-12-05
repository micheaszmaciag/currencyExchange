from rest_framework import serializers
from currencyData.models import Currency


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['code']

# Placeholder for future use

# class CurrencyRateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Currency
#         fields = ['rate']