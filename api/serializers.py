from rest_framework import serializers
from currencyData.models import Currency


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['code']

# I keep in case I will build some filter

# class CurrencyRateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Currency
#         fields = ['rate']