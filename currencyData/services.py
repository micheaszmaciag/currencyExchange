import requests
import pandas
from .models import CurrencyHistoryBid, Transaction

NBP_API = 'https://api.nbp.pl/api/exchangerates/tables/c/'


def get_today_and_last_30_days(start_date='', end_date=''):
    """
    Calculates a 30-day date range, ensuring both start and end dates fall on working days (Mon-Fri).

    If dates are on weekends, they are adjusted to the previous Friday.

    :return: tuple dates (start_date, end_date) as working days
    """
    # Placeholder for future use
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
    today = (pandas.Timestamp.now().normalize() - pandas.offsets.BDay(1).date() if pandas.Timestamp.now().weekday() >= 5 else pandas.Timestamp.now().normalize().date())

    # take currency actual code and rate from NBP API
    try:
        data = requests.get(f'{NBP_API}{today}/')
        if data.status_code == 200:
            if 'rates' in data.json()[0]:
                return {currency['code']: currency['bid'] for currency in data.json()[0]['rates']}
            else:
                return {'error': f'There is no rates in {data.json()[0]["rates"]}'}
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
            raise ({'error': f'Connection error {data.status_code}'})


def fetch_historical_rate():
    '''
    Fetches historical exchange rates for all transactions and calculates
    the exchange rate for currency pairs


    :return: None
    '''
    transactions = Transaction.objects.all()
    result = []

    for pair in transactions:
        currency = process_rates(pair.name[0:3])
        quote_currency = process_rates(pair.name[3:])

        combined_rates = [
            (date, rate / quote_currency[date]) for date, rate in currency.items() if date in quote_currency

        ]

        save_historical_data(pair.name, combined_rates)


def save_transaction(code):
    '''
    Saves a currency pair code (e.g., 'USDEUR') to the database as a single string.
    '''
    Transaction.objects.get_or_create(
        name=code
    )


def save_historical_data(symbol, historical_data):
    '''
    :param symbol: Taking pair or currency as symbol
    :param historical_data: Filtered dict of historic dates and rates from Yahoo API
    '''
    transaction, created = Transaction.objects.get_or_create(name=symbol)

    for date, rate in historical_data:
        CurrencyHistoryBid.objects.get_or_create(
            transaction_name=transaction,
            history_transaction_rate=rate,
            history_date=date
        )
