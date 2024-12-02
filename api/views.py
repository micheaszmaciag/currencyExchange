import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CurrencySerializer
from currencyData.models import Currency
from currencyData.services import fetch_historical_rate, save_historical_data


@api_view(['GET'])
def getRoutes(request):
    routes = [
        {'GET': '/currency/',
         'description': 'list of all currencies',
         'filters': {
             'code': 'Filter by currency code ( e.g: /currency/?code=USD ) or a single letter to find matching currencies (e.g. /currency/?code=U/ will return USD, AUD, etc.).',
             'min_rate': 'Minimum rate value ( e.g., /currency/?min_rate=1.0 )',
             'max_rate': 'Maximum rate value ( e.g., /currency/?max_rate=1.5 )',
             'min_rate&max_rate': 'Returns values between the minimum and maximum rates ( e.g., /currency//?min_rate=1.5&max_rate=3 )',
             'sort_by & order': 'Returns sorted values by ASC or DESC available sort values (code, rate_currency ) (e.g of use /currency/?sort_by=code&order=ASC) '
         }
         },

        {'GET': '/currency/EUR/USD/',
         'description': 'returns exchange rate of value (ex: /currency/EUR/USD/)'
         },
    ]

    return Response(routes)


@api_view(['GET'])
def getCurrency(request):
    code = request.GET.get('code')
    order = request.GET.get('order')
    sort_by = request.GET.get('sort_by')
    min_rate = request.GET.get('min_rate')
    max_rate = request.GET.get('max_rate')

    currency = Currency.objects.all()

    if code:
        currency = currency.filter(code__icontains=code)
    if min_rate:
        try:
            min_rate_value = float(min_rate)
            currency = currency.filter(rate_currency__gte=min_rate_value)
        except ValueError:
            return Response({'error': 'min_rate must be a number e.g: 1.0 or 2.5'})
    if max_rate:
        try:
            max_rate_value = float(max_rate)
            currency = currency.filter(rate_currency__lte=max_rate_value)
        except ValueError:
            return Response({'error': 'max_rate must be a number e.g: 1.0 or 2.5'})

    if sort_by:
        try:
            valid_sort_fields = ['code', 'rate_currency']
            if sort_by in valid_sort_fields:
                if order == 'desc':
                    sort_by = f'-{sort_by}'
                currency = currency.order_by(sort_by)
        except ValueError:
            return Response({'error': f'Invalid poll of sort. Available one: {valid_sort_fields}'})

    serializer = CurrencySerializer(currency, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getCurrencyRate(request, base_currency, quote_currency):
    try:
        first_currency = Currency.objects.get(code=base_currency.upper())
        second_currency = Currency.objects.get(code=quote_currency.upper())
    except:
        return Response({
            'error': 'One of the entered values does not exist or is input incorrectly. Example of a correct format: /currency/EUR/USD/'})

    try:
        rate = round(first_currency.rate_currency / second_currency.rate_currency, 3)
        result = {'currency_pair': f'{base_currency.upper()}{quote_currency.upper()}', 'exchange_rate': rate}
    except ZeroDivisionError:
        return Response({'error': 'One of the value could be a 0 we cannot divide by 0'})

    try:
        symbol = base_currency.upper() + quote_currency.upper()
        #
        historical_data = fetch_historical_rate(symbol)
        save_historical_data(symbol, historical_data)

    except Exception as error:
        return Response({'error': f'Raise error: {str(error)}'})


    return Response(result)
