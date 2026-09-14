from ast import excepthandler

from sqlalchemy import text

PORTFOLIO_NAME = 'demo_growth_14_09_2026'

TRANSACTIONS = [
    ('AAPL', '2026-06-01', 'buy',  25, 195.00),
    ('MSFT', '2026-06-15', 'buy',  15, 415.00),
    ('COST', '2026-07-01', 'buy',  10, 850.00),
    ('AAPL', '2026-07-20', 'buy',  10, 200.00),   # 2nd AAPL buy -> tests accumulation
    ('MSFT', '2026-08-10', 'sell',  5, 430.00),   # partial sell -> tests reduction
]

DIVIDENDS = [('AAPL', '2026-08-25', 8.75)]

INSERT_PORTFOLIO = text("""
    INSERT INTO portfolios (name)
    VALUES (:name)
    RETURNING id
""")

INSERT_TRANSACTION = text("""
    INSERT INTO transactions (portfolio_id, instrument_id, txn_date, txn_type, quantity, price, amount)
    VALUES (:portfolio_id, :instrument_id, :txn_date, :txn_type, :quantity, :price, :amount)
""")

def get_instrument_id(conn, symbol):
    return conn.execute(
        text('SELECT id FROM instruments WHERE symbol = :symbol'),
        {'symbol': symbol}
    ).scalar()

def seed_portfolio(engine):
    with engine.begin() as conn:
        portfolio_id = conn.execute(INSERT_PORTFOLIO, {'name': PORTFOLIO_NAME}).scalar()
        print(f'Created portfolio "{PORTFOLIO_NAME}" ({portfolio_id})')

        for symbol, date, txn_type, qty, price in TRANSACTIONS:
            print(f'Entering transaction for {symbol}')
            instrument_id = get_instrument_id(conn, symbol)
            if instrument_id is None:
                print(f'Skipping {symbol}, not found in table')
                continue
            amount = round(qty * price, 2)
            try:
                conn.execute(INSERT_TRANSACTION, {
                    'portfolio_id': portfolio_id, 'instrument_id': instrument_id, 'txn_date': date,
                    'txn_type': txn_type, 'quantity': qty, 'price': price, 'amount': amount,
                })
                print(f'\t{txn_type.upper():5} {qty:>3} {symbol} @ {price:>7} on {date}')
            except Exception as e:
                print(f'Failed to insert transaction:\n\t{txn_type.upper():5} {qty:>3} {symbol} @ {price:>7} on {date}\n{e}')
                continue

        for symbol, date, amount in DIVIDENDS:
            instrument_id = get_instrument_id(conn, symbol)
            if instrument_id is None:
                print(f'Skipping {symbol}, not found in table')
                continue
            try:
                conn.execute(INSERT_TRANSACTION, {
                    'portfolio_id': portfolio_id, 'instrument_id': instrument_id, 'txn_date': date,
                    'txn_type': 'dividend', 'quantity': None, 'price': None, 'amount': amount,
                })
            except Exception as e:
                print(f'Failed to insert transaction:\n\\tDIVDEND {symbol} +${amount} on {date}\n{e}')
                continue
            print(f'\tDIVDEND {symbol} +${amount} on {date}')
