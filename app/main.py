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
from .reconstruct_holdings import reconstruct_holdings

def do_fetch_ingest():
    print('Start DB engine')

    db_engine = get_engine()

    # print('Fetch and ingest prices')
    # seed_portfolio(db_engine)
    # ingest(db_engine)
    # seed(db_engine, ['AAPL', 'MSFT', 'COST', 'WK', 'VTI', 'GOOGL'])
    reconstruct_holdings(db_engine)
    print('Complete')

do_fetch_ingest()

# import yfinance as yf

# ticker_symbol = "VGT"

# # Create a Ticker object
# ticker = yf.Ticker(ticker_symbol)

# print('\nInfo:')
# print(ticker.info['longName'])

# # print('\nFast-Info:')
# # print(ticker.fast_info)
# try:
#     print('\nFunds Data:')
#     print(ticker.funds_data.description)
    
#     print('\nFund Overview:')
#     print(ticker.funds_data.fund_overview)
    
#     print('\nAsset Classes:')
#     print(ticker.funds_data.asset_classes)
    
#     print('\nBond Holdings:')
#     print(ticker.funds_data.bond_holdings)
    
#     print('\nEquity Holdings:')
#     print(ticker.funds_data.equity_holdings)
    
#     print('\nSector Weightings:')
#     print(ticker.funds_data.sector_weightings)
    
#     print('\nTop Holdings:')
#     print(ticker.funds_data.top_holdings)

# except Exception as e:
#     print('Not a fund')
    
    


