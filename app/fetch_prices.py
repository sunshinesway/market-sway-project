import yfinance as yf
from sqlalchemy import text

SELECT_QUERY = text("""
    SELECT id, symbol FROM instruments
    WHERE is_active = True;
""")

# TODO: change to DO UPDATE for CONFLICTs
INSERT_QUERY = text("""
    INSERT INTO prices (instrument_id, price_date, open, high, low, close, volume)
    VALUES (:instrument_id, :price_date, :open, :high, :low, :close, :volume)
    ON CONFLICT (instrument_id, price_date) DO NOTHING
""")

def get_instruments(conn) -> dict:
    result = conn.execute(SELECT_QUERY)
    return result

def fetch_prices(ticker: str):
    price_data = yf.Ticker(ticker).history(period='1d', actions=False)
    # print('Price data: \n')
    # print(price_data)
    return price_data
    
def convert_data(price_data, id) -> dict:
    return {
        'instrument_id': id,
        'price_date': price_data.index[0].date(),
        'open': float(price_data['Open'].iloc[0]),
        'high': float(price_data['High'].iloc[0]),
        'low': float(price_data['Low'].iloc[0]),
        'close': float(price_data['Close'].iloc[0]),
        'volume': int(price_data['Volume'].iloc[0])
    }
    
def insert_prices(engine):
    with engine.begin() as conn:
        instrument_ids = get_instruments(conn).fetchall()
        print(instrument_ids)

        tickers = []
        for row in instrument_ids:
            tickers.append(row.symbol)
            print(f'Symbol: {row.symbol}\tID: {row.id}')

        price_rows = [convert_data(fetch_prices(t),id) for id, t in instrument_ids]
        
        for row in price_rows:
            print(row)

        conn.execute(INSERT_QUERY, price_rows)
