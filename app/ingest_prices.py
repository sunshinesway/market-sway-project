import yfinance as yf
from sqlalchemy import text

INSERT_START_I_R_QUERY = text("""
    INSERT INTO ingestion_runs (source)
    OUTPUT INSERTED.id
    VALUES(:source);
""")


INSERT_COMPLETE_I_R_QUERY = text("""
    UPDATE ingestion_runs (id, finished_at, rows_ingested, status, error_message)
    SET 
    VALUES (:finished_at, :rows_ingested, :status, :error_message)
    WHERE ingestion_runs.id IS 

""")
SELECT_INSTRUMENTS_QUERY = text("""
    SELECT symbol, id FROM instruments
    WHERE is_active = True;
""")

# TODO: change to DO UPDATE for CONFLICTs
INSERT_PRICE_QUERY = text("""
    INSERT INTO prices (instrument_id, price_date, open, high, low, close, volume)
    VALUES (:instrument_id, :price_date, :open, :high, :low, :close, :volume)
    ON CONFLICT (instrument_id, price_date) DO UPDATE
        SET
            open           = EXCLUDED.open,
            high           = EXCLUDED.high,
            low            = EXCLUDED.low,
            close          = EXCLUDED.close,
            adjusted_close = EXCLUDED.adjusted_close,
            volume         = EXCLUDED.volume,
            source         = EXCLUDED.source,
            ingested_at    = now()
        WHERE
            prices.close            IS DISTINCT FROM EXCLUDED.close
            OR prices.adjusted_close IS DISTINCT FROM EXCLUDED.adjusted_close
            OR prices.open          IS DISTINCT FROM EXCLUDED.open
            OR prices.high          IS DISTINCT FROM EXCLUDED.high
            OR prices.low           IS DISTINCT FROM EXCLUDED.low
            OR prices.volume        IS DISTINCT FROM EXCLUDED.volume;
""")

def get_instruments(conn) -> dict:
    result = conn.execute(SELECT_INSTRUMENTS_QUERY)
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

def insert_prices(conn, price_rows):

        conn.execute(INSERT_PRICE_QUERY, price_rows)

def ingest(engine):
    # TODO: start ingestion run - create row in ingestion_runs table - source: yfinance

    with engine.begin() as conn:
        # create ingestion run row, start I_R
        

        # get ids of available instruments in table
        instrument_ids = {}
        try:
            instrument_ids = get_instruments(conn).fetchall()
            print(instrument_ids)
        except Exception as e:
            print(f'ERROR PULLING INSTRUMENTS FROM TABLE\n{e}')

        # get ticker symbols for instruments
        # tickers = []
        # for row in instrument_ids:
        #     tickers.append(row.symbol)
        #     print(f'Symbol: {row.symbol}\tID: {row.id}')

        # get price history from YF
        # convert data to table format
        price_rows = []
        for t, id in instrument_ids:
            try:
                p_d = fetch_prices(t)
                price_rows.append(convert_data(p_d, id))
            except Exception as e:
                print(f'ERROR FETCHING SYMBOL {t}\n{e}')
                continue

        try:
            insert_prices(conn, price_rows)
        except Exception as e:
            print(f"ERROR INSERTING PRICES INTO TABLE\n{e}")

    # TODO: complete ingestion run - finished, rows ingested, status, error
