# Seed instruments into db

import yfinance as yf
from sqlalchemy import text

INSERT_QUERY = text("""
    INSERT INTO instruments (symbol, name, asset_class, currency, is_active)
    VALUES (:symbol, :name, :asset_class, :currency, :is_active)
    ON CONFLICT (symbol) DO NOTHING
""")
TICKERS = ['AAPL', 'MSFT', 'COST', 'WK', 'VTI', 'GOOGL']

def fetch_info(ticker: str) -> dict:
    info = yf.Ticker(ticker).info
    return {
        'symbol': ticker, 
        'name': info.get('shortName'), 
        'asset_class': info.get('quoteType'), 
        'currency': info.get('currency'), 
        'is_active': info.get('regularMarketPrice') is not None
    }
    
def seed(engine, tickers=TICKERS):
    rows = [fetch_info(t) for t in tickers]

    with engine.begin() as conn:
        conn.execute(INSERT_QUERY, rows)

    print(f'Seeded {len(rows)} instruments (any existing symbols were skipped)')
