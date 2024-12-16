from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from currencyData.models import Currency
from currencyData.services import save_transaction


@api_view(['GET'])
def getRoutes(request):
    routes = [
        {'GET': '/currency/EUR/USD/',
         'description': 'returns exchange rate of value (e.g. : /currency/EUR/USD/)'
         },
    ]

    return Response(routes)


@api_view(['GET'])
def getCurrencyRate(request, base_currency, quote_currency):
    '''
     Fetches the exchange rate for a currency pair and saves the transaction.

    args:
        base_currency (str): The base currency code (e.g., 'EUR').
        quote_currency (str): The quote currency code (e.g., 'USD').


    return:
        Response: A dictionary containing the currency pair and the exchange rate
    '''
    try:
        first_currency = Currency.objects.get(code=base_currency.upper())
        second_currency = Currency.objects.get(code=quote_currency.upper())
    except Exception as error:
        return Response({
            'error': f'One of the entered currency codes does not exist. Example format: /currency/EUR/USD/ {error}'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        rate = (first_currency.rate_currency / second_currency.rate_currency)
        result = {'currency_pair': f'{base_currency.upper()}{quote_currency.upper()}', 'exchange_rate': rate}
    except ZeroDivisionError:
        return Response({
            'error': 'The quote currency rate is 0. Division by zero is not allowed'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        symbol = base_currency.upper() + quote_currency.upper()
        if len(symbol) == 6:
            save_transaction(symbol.upper())
    except Exception as error:
        return Response({
            'error': f'An error occurred while saving the transaction: {str(error)}'
        }, status=status.HTTP_400_BAD_REQUEST)

    return Response(result)
