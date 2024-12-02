from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import CurrencySerializer, CurrencyRateSerializer
from currencyData.models import Currency

@api_view(['GET'])
def getRoutes(request):

    routes = [
        {'GET': '/currency/'},
        {'GET': '/currency/EUR/USD/'},
    ]

    return Response(routes)

@api_view(['GET'])
def getCurrency(request):
    currency = Currency.objects.all().order_by('code')
    serializer = CurrencySerializer(currency, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getCurrencyRate(request, currency, second):
    first_currency = Currency.objects.get(code=currency.upper())
    second_currency = Currency.objects.get(code=second.upper())
    rate = round(first_currency.rate_currency / second_currency.rate_currency, 3)

    result = {'currency_pair': f'{currency.upper()}{second.upper()}', 'exchange_rate': rate}

    return Response(result)