import requests
import pandas as pd
import yfinance as yf

NBP_API = 'https://api.nbp.pl/api/exchangerates/tables/c/'


def get_currency():
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
def fetch_rate_now(ticker_symbol='EURPLN=X', period='1d'):
    currency_pair = yf.Ticker(ticker_symbol)
    data = currency_pair.history(period)

    df = pd.DataFrame(data)
    return {ticker_symbol[:6]: [(str(date)[0:10]), rate] for date,rate in df['High'].to_dict().items()}


