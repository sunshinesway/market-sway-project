# use historical portfolio transactions to determine
# instruments on any specified date


from sqlalchemy import text
from .transaction import Transaction
from .portfolio import Portfolio


# get portfolios
SELECT_PORTFOLIOS_QUERY = text("""
    SELECT id, name, base_currency FROM portfolios;
""")
# get transaction for portfolio
SELECT_TRANSACTIONS_QUERY = text("""
    SELECT id, portfolio_id, instrument_id, txn_date, txn_type, quantity, price, amount FROM transactions
    WHERE portfolio_id = :portfolio_id;
""")
# get instrument symbol
SELECT_INSTRUMENT_QUERY = text("""
    SELECT symbol FROM instruments
    WHERE id = :instrument_id;
""")

def get_portfolios(engine) -> dict:
    try:
        with engine.begin() as conn:
            result = conn.execute(SELECT_PORTFOLIOS_QUERY)
            return result
    except Exception as e:
        print(f'ERROR GETTING PORTFOLIOS\n{e}')

def get_transactions(engine, portfolio_id):
    try:
        with engine.begin() as conn:
            result = conn.execute(SELECT_TRANSACTIONS_QUERY, {'portfolio_id': portfolio_id})
            return result
    except Exception as e:
        print(f'ERROR GETTING TRANSACTIONS\n{e}')

def get_instrument_symbol(engine, instrument_id):
    try:
        with engine.begin() as conn:
            result = conn.execute(SELECT_INSTRUMENT_QUERY, {'instrument_id': instrument_id})
            return result
    except Exception as e:
        print(f'ERROR GETTING INSTRUMENT\n{e}')

def reconstruct_holdings(engine): # returns portfolio objects
    print('Fetching portfolios from DB . . .')
    p_s = get_portfolios(engine)
    print(f'Fetched {p_s.rowcount} portfolio(s) from DB')

    portfolios = []
    for p in p_s:
        print(f'Fetching transactions for portfolio {p.name} . . .')
        transactions = get_transactions(engine, p.id)
        print(f'Fetched {transactions.rowcount} transaction(s) from DB'
        )
        p_trans: list[Transaction] = []
        print(f'type of p_trans: {type(p_trans)}')
        # TODO: create Portfolio object, save transactions there to calc holdings
        for t in transactions:
            s = get_instrument_symbol(engine, t.instrument_id)
            symbol = s.fetchone().symbol
            transaction = Transaction(t.id, t.portfolio_id, t.instrument_id, symbol, t.txn_date, t.txn_type, t.quantity, t.price, t.amount)
            print(f'Transaction created: {transaction}')
            # print(transaction.txn_type)
            # if symbol in p_trans:
            #     p_trans[symbol].append(transaction)
            # else: p_trans[symbol] = [transaction]
            p_trans.append(transaction)

        portfolios.append(Portfolio(p.id, p.name, p.base_currency, p_trans))
    
    for p in portfolios:
        print(p)
    return portfolios
