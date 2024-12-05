from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import CurrencySerializer
from currencyData.models import Currency
from currencyData.services import save_transaction


@api_view(['GET'])
def getRoutes(request):
    routes = [
        {'GET': '/currency/',
         'description': 'list of all currencies',
         'filters': {
             'code': 'Filter by currency code ( e.g : /currency/?code=USD ) or a single letter to find matching currencies '
                     '(e.g. /currency/?code=U/ will return USD, AUD, etc.).',
             'min_rate': 'Minimum rate value ( e.g. : /currency/?min_rate=1.0 )',
             'max_rate': 'Maximum rate value ( e.g. : /currency/?max_rate=1.5 )',
             'min_rate&max_rate': 'Returns values between the minimum and maximum rates ( e.g. : /currency/?min_rate=1.5&max_rate=3 )',
             'sort_by & order': 'Returns sorted values by ASC or DESC available sort values (code, rate_currency ) (e.g of use : /currency/?sort_by=code&order=ASC) '
         }
         },

        {'GET': '/currency/EUR/USD/',
         'description': 'returns exchange rate of value (e.g. : /currency/EUR/USD/)'
         },
    ]

    return Response(routes)


@api_view(['GET'])
def getCurrency(request):
    '''
    Retrieves a list of currencies from the database.

    Query Parameters:
        - code (str): Filter currencies by code
        - order (str): Sorting order ('asc' or 'desc').
        - sort_by (str): Field to sort by ('code' or 'rate_currency').
        - min_rate (float): Minimum rate for filtering.
        - max_rate (float): Maximum rate for filtering.
    '''
    code = request.GET.get('code')
    order = request.GET.get('order', 'asc').lower()
    sort_by = request.GET.get('sort_by')
    min_rate = request.GET.get('min_rate')
    max_rate = request.GET.get('max_rate')

    currency = Currency.objects.all()

    if code:
        currency = currency.filter(code__icontains=code)
    if min_rate and max_rate:
        if float(min_rate) > float(max_rate):
            return Response({
                'error': f'min_rate: ({min_rate}) cannot be greater than max_rate: ({max_rate}).'
            }, status=status.HTTP_400_BAD_REQUEST)
    if min_rate:
        try:
            min_rate_value = float(min_rate)
            currency = currency.filter(rate_currency__gte=min_rate_value)
        except ValueError:
            return Response({
                'error': "'min_rate' must be a valid decimal number. Example: ?min_rate=1.0"
            }, status=status.HTTP_400_BAD_REQUEST)
    if max_rate:
        try:
            max_rate_value = float(max_rate)
            currency = currency.filter(rate_currency__lte=max_rate_value)
        except ValueError:
            return Response({
                'error': "'max_rate' must be a valid decimal number. Example: ?max_rate=1.0"
            }, status=status.HTTP_400_BAD_REQUEST)

    if sort_by:
        valid_sort_fields = ['code']
        print(sort_by)
        if sort_by not in valid_sort_fields:
            return Response({
                'error': f"'sort_by' must be one of the following fields: {', '.join(valid_sort_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        valid_orders = ['asc', 'desc']
        if order not in valid_orders:
            return Response({
                'error': "Invalid value for 'order'. Use 'asc' or 'desc'."
            }, status=status.HTTP_400_BAD_REQUEST)

        sort_field = f'-{sort_by}' if order == 'desc' else sort_by
        currency = currency.order_by(sort_field)

    serializer = CurrencySerializer(currency, many=True)
    return Response(serializer.data)


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
