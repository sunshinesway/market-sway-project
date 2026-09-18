

class Transaction:
    def __init__(self, id, portfolio_id, instrument_id, symbol, txn_date, txn_type, quantity, price, amount):
        self.id = id
        self.portfolio_id = portfolio_id
        self.instrument_id = instrument_id
        self.symbol = symbol
        self.txn_date = txn_date
        self.txn_type = txn_type
        self.quantity = quantity
        self.price = price
        self.amount = amount

    def __str__(self):
        return f'tick: {self.symbol}\ttxn_date: {self.txn_date}\ttxn_type: {self.txn_type}\tamt: {self.amount}\tprice: {self.price}\tquantity: {self.quantity}'