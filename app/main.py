# from fastapi import FastAPI

# app = FastAPI()

# @app.get('/')
# def read_root():
#     return {'Hello': 'World'}

# @app.get('/items/{item_id}')
# def read_item(item_id: int, q: str | None = None):
#     return {'item_id': item_id, 'q': q}
from .db_connection import get_engine
from .seed_instruments import seed
from .fetch_prices import insert_prices
print('hello world')


db_engine = get_engine()
# print(db_conn)
# seed(db_engine)
insert_prices(db_engine)

print('2hello world2')
# import yfinance as yf

# ticker_symbol = "AAPL"

# # Create a Ticker object
# ticker = yf.Ticker(ticker_symbol)

# print('\nInfo:')
# print(ticker.info['longName'])

# print('\nFast-Info:')
# print(ticker.fast_info)

