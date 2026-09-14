# Seed instruments into db

import yfinance as yf
from sqlalchemy import text
from os import error

INSERT_QUERY = text("""
    INSERT INTO instruments (symbol, name, asset_class, currency, is_active)
    VALUES (:symbol, :name, :asset_class, :currency, :is_active)
    ON CONFLICT (symbol) DO NOTHING
    RETURNING symbol, id;
""")
TICKERS = ['AAPL', 'MSFT', 'COST', 'WK', 'VTI', 'GOOGL']

INSERT_START_I_R_QUERY = text("""
    INSERT INTO ingestion_runs (source)
    VALUES(:source)
    RETURNING id;
""")
UPDATE_COMPLETE_I_R_QUERY = text("""
    UPDATE ingestion_runs
    SET
        finished_at     = now(),
        rows_ingested   = :rows_ingested,
        status          = :status,
        error_message   = :error_message
    WHERE id = :id;

""")
SELECT_INSTRUMENTS_QUERY = text("""
    SELECT symbol, id FROM instruments
    WHERE is_active = True;
""")
INSERT_PRICE_QUERY = text("""
    INSERT INTO prices (instrument_id, price_date, open, high, low, close, volume, source)
    VALUES (:instrument_id, :price_date, :open, :high, :low, :close, :volume, :source)
    ON CONFLICT (instrument_id, price_date) DO UPDATE
        SET
            open           = EXCLUDED.open,
            high           = EXCLUDED.high,
            low            = EXCLUDED.low,
            close          = EXCLUDED.close,
            volume         = EXCLUDED.volume,
            source         = EXCLUDED.source,
            ingested_at    = now()
        WHERE
            prices.close            IS DISTINCT FROM EXCLUDED.close
            OR prices.open          IS DISTINCT FROM EXCLUDED.open
            OR prices.high          IS DISTINCT FROM EXCLUDED.high
            OR prices.low           IS DISTINCT FROM EXCLUDED.low
            OR prices.volume        IS DISTINCT FROM EXCLUDED.volume;
""")

def fetch_info(ticker: str) -> dict:
    info = yf.Ticker(ticker).info
    return {
        'symbol': ticker,
        'name': info.get('shortName'),
        'asset_class': info.get('quoteType'),
        'currency': info.get('currency'),
        'is_active': info.get('regularMarketPrice') is not None
    }

def format_error(e: Exception, max_len:int = 300) -> str:
    # SQL alchemy error messages are a nightmore, reformatting
    error_message = str(getattr(e, 'orig', e)).strip()
    if len(error_message) > max_len:
        error_message = message[:max_len].rstrip() + '. . .'
    return error_message

def fetch_prices(ticker: str):
    price_data = yf.Ticker(ticker).history(period='ytd',actions=False)
    # print('Price data: \n')
    # print(price_data)
    if price_data.empty:
        raise ValueError(f'NO PRICE DATA RETURNED FOR {ticker}')

    return price_data

def convert_data(price_data, id, source, index) -> dict:
    return {
        'instrument_id': id,
        'price_date': price_data.index[index].date(),
        'open': float(price_data['Open'].iloc[index]),
        'high': float(price_data['High'].iloc[index]),
        'low': float(price_data['Low'].iloc[index]),
        'close': float(price_data['Close'].iloc[index]),
        'volume': int(price_data['Volume'].iloc[index]),
        'source': source
    }

def insert_prices(engine, price_rows):
    with engine.begin() as conn:
        conn.execute(INSERT_PRICE_QUERY, price_rows)
    print('INSERTED!')

def complete_run(engine, run_id, rows_ingested, status, error_message):
    try:
        with engine.begin() as conn:
            update_res = conn.execute(UPDATE_COMPLETE_I_R_QUERY, {'id':run_id,'rows_ingested': rows_ingested, 'status': status, 'error_message': error_message})

        if update_res == 0: print(f'NO INGESTION RUN FOUND FOR ID={run_id}')
    except Exception as e:
        print(f'ERROR COMPLETING INGESTION RUN ID={run_id}:\t{e}')

# adjusted from ingest_prices to take a single instrumemt
def ingest(engine, instrument): 
    # create ingestion run row, start I_R, get I_R id
    source = 'yfinance'
    # error_message = None
    # rows_ingested = 0
    # status = 'success'
    # try:
    #     with engine.begin() as conn:
    #         run_id = conn.execute(INSERT_START_I_R_QUERY, {'source': source}).scalar()
    # except Exception as e:
    #     print(f'ERROR INSERTING NEW I_R ROW\n{e}')
    #     return # fatal error: abort ingestion_run
    # print('1: Started I_R: ', run_id)

    # get price history from YF
    # convert data to table format
    price_rows = []
    # for row in instrument_ids:
    try:
        p_d = fetch_prices(instrument.symbol) # get price data
        print('FETCHED PRICE DATA')
        for i in range(len(p_d.index)):
            # print(f'i: {i}, ', end='')
            price_rows.append(convert_data(p_d, instrument.id, source, i))
        print()
        # print(price_rows)
    except Exception as e:
        print(f'ERROR FETCHING SYMBOL {instrument.symbol}:\t{e}')
    # print('3: Prices fetched, converted')

    try:
        print('# price_rows=',len(price_rows))
        if price_rows:
            print('INSERTING PRICES')
            insert_prices(engine, price_rows)
        rows_ingested = len(price_rows)
        
    except Exception as e:
        # error_message = format_error(e)
        # status = 'failed'
        print(f"ERROR INGESTING {instrument}: {e}")
        raise
    # print('4. Prices inserted in DB')
    # complete ingestion run record
    # complete_run(engine, run_id, rows_ingested, status, error_message)

#     # print(f'5. Completed I_R: {run_id}, status: {status}')

def seed(engine, tickers=TICKERS):
    rows = [fetch_info(t) for t in tickers]

    for r in rows:
        with engine.begin() as conn:
            result = conn.execute(INSERT_QUERY, r)
            instrument = result.fetchone()
            
            print(instrument)
            print(instrument.symbol)
            print(instrument.id)
            # # ingest YTD price data for new instruments:
            # # ingest prices for each ticker
        with engine.begin() as conn:
            ingest(engine, instrument)

    print(f'Seeded {len(rows)} instruments (any existing symbols were skipped)')

    



