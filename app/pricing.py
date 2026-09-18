from sqlalchemy import text
from datetime import date

# get price of instrument on specified datee
SELECT_INSTRUMENT_PRICE_QUERY = text("""
    SELECT p.open as open, p.high as high, p.low as low, p.close as close, p.volume as volume
    FROM instruments as i
    JOIN prices as p
        ON i.id = p.instrument_id
    WHERE p.price_date = :date;
""")
def get_price(engine, symbol, date):
    try:
        with engine.begin() as conn:
            result = conn.execute(SELECT_INSTRUMENT_PRICE_QUERY, {'date': date}).fetchone().close
            return result
    except Exception as e:
        print(f'ERROR FETCHING PRICE FOR SYMBOL {symbol} on date {date}:\n{e}')

# return value of instrument in a portfolio
def calc_value(engine, symbol, quantity, date=date.today()):
    close_price = get_price(engine, symbol, date)

    print(f'\tPrice: {round(close_price,2)}\tQuantity: {quantity}')
    value = round(close_price * quantity, 2)
    print(f'\tValue: ${value}')
