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
from .ingest_prices import ingest
from .seed_portfolio import seed_portfolio

def do_fetch_ingest():
    print('Start DB engine')

    db_engine = get_engine()

    print('Fetch and ingest prices')
    # seed_portfolio(db_engine)
    ingest(db_engine)
    # seed(db_engine, ['AAPL', 'MSFT', 'COST', 'WK', 'VTI', 'GOOGL'])
    
    print('Complete')

do_fetch_ingest()

# import yfinance as yf

# ticker_symbol = "AAPL"

# # Create a Ticker object
# ticker = yf.Ticker(ticker_symbol)

# print('\nInfo:')
# print(ticker.info['longName'])

# print('\nFast-Info:')
# print(ticker.fast_info)
