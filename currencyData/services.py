import requests
import pandas as pd
import yfinance as yf
import datetime
from .models import CurrencyHistoryBid

NBP_API = 'https://api.nbp.pl/api/exchangerates/tables/c/'


def get_currency():
    '''
    :return: Names and rates from Tables C from NBP API
    '''
    # take currency code and rate from NBP API
    try:
        data = requests.get(NBP_API)
        if data.status_code == 200:
            if 'rates' in data.json()[0]:
                return {currency['code']: currency['bid'] for currency in data.json()[0]['rates']}
            else:
                return []
    except:
        print(f'Something Went Wrong {data.status_code}')
        return []

# WILL USE IN THE FUTURE TO FETCH HISTORY OF PAST CURRENCY EXCHANGE
def fetch_historical_rate(ticker_symbol='EURPLN', period='1mo'):
    '''
     Fetch historical exchange rates for a given ticker symbol from django API

    :param ticker_symbol: Currency pair in the format 'EURPLN' (6 characters)
    :param period: Time period for historical data
    :return: Dictionary with transaction dates and rates, or error message.
    '''

    try:
        if len(ticker_symbol) == 6:
            end = '=X'
            currency_pair = yf.Ticker(ticker_symbol.upper()+end)
            data = currency_pair.history(period)
            if not data.empty:
                df = pd.DataFrame(data)
                return {transactionDate.date(): round(rate,3) for transactionDate, rate in df['Close'].to_dict().items()
                                           if isinstance(transactionDate.date(), datetime.date) and isinstance(rate, float)}

            if data.empty:
                raise ValueError(f'No data for {ticker_symbol}')

        else:
            raise ValueError (f'Wrong value {ticker_symbol}')

    except ValueError as v_error:
        return {'error': str(v_error)}
    except requests.ConnectionError:
        return {'error': 'We have some connection error!'}
    except Exception as error:
        return {'error:' f'Unexpected error occured: {str(error)}'}


def save_historical_data(symbol, historical_data):
    '''

    :param symbol: Taking pair or currency as symbol
    :param historical_data: Filtered dict of historic dates and rates from Yahoo API
    '''

    for date, rate in historical_data.items():
        CurrencyHistoryBid.objects.get_or_create(
            history_transaction_name=symbol,
            history_transaction_rate=rate,
            history_date=date
        )



