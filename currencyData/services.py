import requests
import pandas
from .models import CurrencyExchangeRate, Currency
from .tasks import update_pair_history
from django.core.cache import cache
from openpyxl.utils import get_column_letter
from django.http import HttpResponse

def get_today_and_last_30_days(start_date='', end_date=''):
    """
    Calculates a 30-day date range, ensuring both start and end dates fall on working days (Mon-Fri).

    If dates are on weekends, they are adjusted to the previous Friday.

    :return: tuple dates (start_date, end_date) as working days
    """
    # for future use
    # start_date = pandas.Timestamp(start_date)

    # Get the current day
    end_date = pandas.Timestamp.now().normalize()

    # Current day - 30 calendar working days
    start_date = end_date - pandas.Timedelta(days=30)

    # Ensure sure that is not a weekend
    if end_date.weekday() >= 5:
        end_date = end_date - pandas.offsets.BDay(1)

    # Ensure the start_date (30 days ago) is not a weekend
    if start_date.weekday() >= 5:
        start_date = start_date - pandas.offsets.BDay(1)

    return start_date.date(), end_date.date()


def get_currency():
    '''
    Fetches current currency codes and bid rates
    :return:  dict: A dictionary with currency codes as keys and bid rates as values

    '''
    # fetch current data day. Check that this day is not a Saturday or Sunday.
    today = ((pandas.Timestamp.now().normalize() - pandas.offsets.BDay(1)).date() if pandas.Timestamp.now().weekday() >= 5 else pandas.Timestamp.now().normalize().date())
    NBP_API = 'https://api.nbp.pl/api/exchangerates/tables/c/'
    # take currency code and rate from NBP API
    try:
        data = requests.get(f'{NBP_API}{today}/')
        if data.status_code == 200:
            if 'rates' in data.json()[0]:
                return {currency['code']: currency['bid'] for currency in data.json()[0]['rates']}
            else:
                return {'error': f'There is no rates in {data.json()[0]}'}
    except:
        return {'error': f'Something Went Wrong {data.status_code}'}


def process_rates(code, date_start='', date_end=''):
    '''
    Fetches exchange rates from the NBP API for a given currency code and date range.

    code (str): Currency code (e.g., 'USD', 'EUR', or 'PLN').
    date_start (str): Start date in the format 'YYYY-MM-DD' (default: '2024-11-01').
    date_end (str): End date in the format 'YYYY-MM-DD' (default: '2024-12-04').

    Returns:
        dict: A dictionary with dates as keys and exchange rates as values.
    '''
    start_end_date = get_today_and_last_30_days(date_start, date_end)

    api_url = 'https://api.nbp.pl/api/exchangerates/rates/c/'

    if code == 'PLN':
        # Use EUR to check calendar holidays (market closed days) since PLN is a fixed value of 1.
        url = f'{api_url}eur/{start_end_date[0]}/{start_end_date[1]}/'
        data = requests.get(url)
        if data.status_code == 200:
            return {item['effectiveDate']: 1 for item in data.json()['rates']}

    else:
        url = f'{api_url}{code}/{start_end_date[0]}/{start_end_date[1]}/'
        data = requests.get(url)
        if data.status_code == 200:
            return {item['effectiveDate']: item['bid'] for item in data.json().get('rates')}

        else:
            raise ValueError({'error': f'Connection error {data.status_code}'})


def fetch_historical_rate():
    '''
    Fetches and calculates historical exchange rates for all currency pairs.

    This function retrieves historical exchange rates for all currency pairs stored
    in the database. To optimize performance, it keeps already fetched currency rates
    in memory, ensuring faster access if the same currency is requested again. The
    calculated rates are then saved for each pair.


    :return: None
    '''
    exchange = CurrencyExchangeRate.objects.all()

    # cache dict { 'EUR': {data1:rate1, date2:rate2, ... }, 'USD': { ....} }
    # to avoid many request to the API for same rate which could make slower database save
    rates_stored = {}
    def get_stored_rates(code):
        if code not in rates_stored:
            rates_stored[code] = process_rates(code)
        return rates_stored[code]

    # currency & quote_currency asking get_cached_rates for rates and date. it reduces API request to minimum
    for pair in exchange:
        base_code = pair.currency_exchange_pair[0:3]
        quote_code = pair.currency_exchange_pair[3:]

        currency = get_stored_rates(base_code)
        quote_currency = get_stored_rates(quote_code)

        try:
            combined_rates = [
                (date, rate / quote_currency[date]) for date, rate in currency.items() if date in quote_currency
            ]
            save_historical_data(pair.currency_exchange_pair, combined_rates)
        except Exception as error:
            return f'An error occurred {error}'

def save_transaction(code):
    '''

    This function checks if the base and quote currencies exist in the database. If they exist, it save the currency pair
    to the CurrencyExchangeRate model with the current exchange rate and date, after that celery send task to fetch
    historical rates from 30 working days.

    To avoid sending duplicate task to the Celery queue, a lock mechanism is implemented using Django caching system.

    :return None
    '''

    today = ((pandas.Timestamp.now().normalize() - pandas.offsets.BDay(1)).date() if pandas.Timestamp.now().weekday() >= 5 else pandas.Timestamp.now().normalize().date())
    currency = Currency.objects.get(code=code[0:3])
    try:
        quote_currency = Currency.objects.get(code=code[3:])
    except Exception as error:
        raise ValueError(f"The base currency '{code[:3]}' or the quote currency '{code[3:]}' does not exist. Details: {error}")


    CurrencyExchangeRate.objects.get_or_create(
        currency=currency,
        currency_exchange_pair=code,
        currency_exchange_rate=currency.rate_currency/quote_currency.rate_currency,
        currency_exchange_date=today
    )
    lock_key = f'loading_history:{code}'

    # Used django cache to locking a pair of code (e.g, USDEUR) for 50 sec if someone request for it to many times to protect overload celery queue.
    if not cache.get(lock_key):
        cache.set(lock_key, True, timeout=50)
        update_pair_history.delay()



def save_historical_data(symbol, historical_data):
    '''
    Saves historical exchange rate data for a currency pair.

    historical_data: list of tuples, each containing a date (str) and rate (float).
    '''

    base_currency = Currency.objects.get(code=symbol[:3])
    for date, rate in historical_data:
        CurrencyExchangeRate.objects.get_or_create(
            currency_exchange_pair=symbol,
            currency_exchange_date=date,
            defaults={
                'currency_exchange_rate': rate,
                'currency': base_currency,
            }
        )

def generate_excel_currencies(queryset, pair):
    '''
    Function generate an Excel file, includes exchange rate pair, exchange rate , exchange rate date.

    :param queryset: QuerySet, filtered data containing exchange rate details.

    :param pair: str, currency pair (e.g., 'USDEUR')

    :return: HttpResponse, response containing the Excel file for download.
    '''
    # prepare data to export to an Excel file.
    data = list(queryset.values('currency_exchange_pair', 'currency_exchange_rate', 'currency_exchange_date'))
    df = pandas.DataFrame(list(data))
    df.rename(columns={
        'currency_exchange_pair': 'Currency Pair',
        'currency_exchange_rate': 'Exchange Rate',
        'currency_exchange_date': 'Exchange Date',
    }, inplace=True)

    # create trigger to download an Excel file in web browser
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{pair}_exchange_rates.xlsx"'

    with pandas.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=f'Exchange Rates {pair}')
        worksheet = writer.sheets[f'Exchange Rates {pair}']

        # add spaces in Excel file
        for column, column_title in enumerate(df.columns, start=1):
            column_letter = get_column_letter(column)
            worksheet.column_dimensions[column_letter].width = 15

    return response