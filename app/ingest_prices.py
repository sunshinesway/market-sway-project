from os import error

import yfinance as yf
from sqlalchemy import text

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

def format_error(e: Exception, max_len:int = 300) -> str:
    # SQL alchemy error messages are a nightmore, reformatting
    error_message = str(getattr(e, 'orig', e)).strip()
    if len(error_message) > max_len:
        error_message = message[:max_len].rstrip() + '. . .'
    return error_message

def get_instruments(engine) -> dict:
    with engine.begin() as conn:
        result = conn.execute(SELECT_INSTRUMENTS_QUERY)
        return result

def fetch_prices(ticker: str):
    price_data = yf.Ticker(ticker).history(period='1d',actions=False)
    # print('Price data: \n')
    # print(price_data)
    if price_data.empty:
        raise ValueError(f'NO PRICE DATA RETURNED FOR {ticker}')

    return price_data

def convert_data(price_data, id, source) -> dict:
    return {
        'instrument_id': id,
        'price_date': price_data.index[0].date(),
        'open': float(price_data['Open'].iloc[0]),
        'high': float(price_data['High'].iloc[0]),
        'low': float(price_data['Low'].iloc[0]),
        'close': float(price_data['Close'].iloc[0]),
        'volume': int(price_data['Volume'].iloc[0]),
        'source': source
    }

def insert_prices(engine, price_rows):
    with engine.begin() as conn:
        conn.execute(INSERT_PRICE_QUERY, price_rows)

def complete_run(engine, run_id, rows_ingested, status, error_message):
    try:
        with engine.begin() as conn:
            update_res = conn.execute(UPDATE_COMPLETE_I_R_QUERY, {'id':run_id,'rows_ingested': rows_ingested, 'status': status, 'error_message': error_message})

        if update_res == 0: print(f'NO INGESTION RUN FOUND FOR ID={run_id}')
    except Exception as e:
        print(f'ERROR COMPLETING INGESTION RUN ID={run_id}:\t{e}')

def ingest(engine):
    # TODO: start ingestion run - create row in ingestion_runs table - source: yfinance
    # create ingestion run row, start I_R, get I_R id
    source = 'yfinance'
    error_message = None
    rows_ingested = 0
    status = 'success'
    try:
        with engine.begin() as conn:
            run_id = conn.execute(INSERT_START_I_R_QUERY, {'source': source}).scalar()
    except Exception as e:
        print(f'ERROR INSERTING NEW I_R ROW\n{e}')
        return # fatal error: abort ingestion_run
    # print('1: Started I_R: ', run_id)
    # get ids of available instruments in table
    instrument_ids = {}
    try:
        instrument_ids = get_instruments(engine).fetchall()
        print(instrument_ids)
    except Exception as e:
        error_message = f'ERROR PULLING INSTRUMENTS FROM TABLE: {e}'
        complete_run(engine, run_id, rows_ingested, 'failed', error_message)
        return # fatal error: abort ingestion_run
    # print('2: Instruments acquired')
    # get price history from YF
    # convert data to table format
    price_rows = []
    for row in instrument_ids:
        try:
            p_d = fetch_prices(row.symbol) # get price data
            price_rows.append(convert_data(p_d, row.id, source))
        except Exception as e:
            print(f'ERROR FETCHING SYMBOL {row.symbol}:\t{e}')
            continue
    # print('3: Prices fetched, converted')

    try:
        if price_rows:
            insert_prices(engine, price_rows)
        rows_ingested = len(price_rows)
    except Exception as e:
        error_message = format_error(e)
        status = 'failed'

    # print('4. Prices inserted in DB')
    # complete ingestion run record
    complete_run(engine, run_id, rows_ingested, status, error_message)

    # print(f'5. Completed I_R: {run_id}, status: {status}')
