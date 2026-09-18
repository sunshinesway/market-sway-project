from collections import Counter
from datetime import date
from operator import attrgetter
from .transaction import Transaction

class Portfolio:
    def __init__(self, id, name:str, base_currency:str, transactions:list[Transaction]):
        self.id = id
        self.name = name
        self.base_currency = base_currency
        self.transactions = transactions
        self.holdings = self.calc_holdings(self.transactions) # get current holdings

    def __str__(self):
        trans_str = ''
        for t in self.transactions:
            trans_str += f'\n{t}'

        return f'{self.name} / {self.base_currency}:{trans_str}'

    # returns dict {ticker : quantity}
    def calc_holdings(self, transactions:list[Transaction], date=date.today()) -> dict:

        quantities = Counter()
        sorted(transactions, key=attrgetter('txn_date'))

        for t in transactions:
            if t.txn_date > date: break

            if t.txn_type == 'buy':
                quantities[t.symbol] += t.quantity
            if t.txn_type == 'sell':
                quantities[t.symbol] -= t.quantity

        return quantities

