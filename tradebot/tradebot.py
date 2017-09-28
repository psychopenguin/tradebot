import logging
from time import sleep
from bittrex import Bittrex


logging.basicConfig(level=logging.INFO)


def calculate_change(x, y):
    return ((x/y) * 100) - 100


def profit(x, y):
    return x + (x * (y/100.0))


class TradeBot():
    def __init__(self, key=None, secret=None, **kwargs):
        self.exchange = Bittrex(key, secret)
        self.orders = []
        # Default config
        config = {
                'base_currency': 'ETH',
                'min_order': 0.001,
                'sleep_time': 60,
                'profit': 2
                }
        # Update config from object constructor
        config.update(kwargs)
        # Set attributes based on config
        for attr in config.keys():
            setattr(self, attr, config[attr])

    def get_markets(self):
        logging.info(f'Getting markets for {self.base_currency}')
        all_markets = self.exchange.get_markets()['result']
        markets = set()
        for mkt in all_markets:
            if mkt['BaseCurrency'] == self.base_currency:
                markets.add(mkt['MarketName'])
        return markets

    def get_market_data(self):
        mkt_data = []
        for mkt in self.markets:
            logging.info(f'Getting market data for {mkt}')
            data = self.exchange.get_marketsummary(mkt)['result'][0]
            data['Change'] = calculate_change(data['Last'], data['PrevDay'])
            mkt_data.append(data)
        return mkt_data

    def has_balance_to_buy(self):
        logging.info('checking if we have some balance to buy')
        q = self.exchange.get_balance(self.base_currency)
        self.balance = q['result']['Available']
        logging.debug(f'{self.balance}{self.base_currency} available')
        if self.balance >= self.min_order:
            return True
        else:
            return False

    def get_market_to_buy(self):
        self.update()
        sorted_mkt = sorted(self.market_data, key=lambda x: x['Change'])
        return sorted_mkt[0]

    def buy(self, mkt):
        price = mkt['Last']
        qnt = self.balance/price
        order = self.exchange.buy_limit(mkt['MarketName'], qnt, price)
        return(order)

    def update(self):
        logging.info('Updating data')
        self.markets = self.get_markets()
        self.market_data = self.get_market_data()

    def do_trade(self):
        # TODO: buy something
        if self.has_balance_to_buy():
            self.buy(self.get_market_to_buy())
        # TODO: sell stuff
        logging.info(f'Sleeping for {self.sleep_time} seconds')
        sleep(self.sleep_time)

    def run(self):
        logging.info('Starting Bot')
        while True:
            self.do_trade()
