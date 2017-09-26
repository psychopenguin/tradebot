import logging
from threading import Thread
from time import sleep
from bittrex import Bittrex


logging.basicConfig(level=logging.INFO)


def calculate_change(x, y):
    return ((x/y) * 100) - 100


class TradeBot(Thread):
    base_currency = 'ETH'

    def __init__(self, key=None, secret=None, base_currency=base_currency):
        Thread.__init__(self)
        self.exchange = Bittrex(key, secret)
        self.base_currency = base_currency

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
        for mkt in self.get_markets():
            logging.debug(f'Getting market data for {mkt}')
            data = self.exchange.get_marketsummary(mkt)['result'][0]
            data['Change'] = calculate_change(data['Last'], data['PrevDay'])
            mkt_data.append(data)
        return mkt_data

    def update(self):
        logging.info('Updating data')
        self.markets = self.get_markets()
        self.market_data = self.get_market_data()

    def get_big_drop(self):
        return sorted(self.market_data, key=lambda x: x['Change'])[0]

    def get_big_spike(self):
        return sorted(self.market_data, key=lambda x: x['Change'])[-1]

    def run(self):
        while True:
            self.update()
            logging.info('sleeping...')
            sleep(60)
