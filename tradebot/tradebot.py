import logging
from time import sleep
from bittrex import Bittrex


logging.basicConfig(level=logging.INFO)


def calculate_change(x, y):
    try:
        change = ((x/y) * 100) - 100
    except ZeroDivisionError:
        change = 0
    return change


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
                'max_order': 0.05,
                'sleep_time': 60,
                'profit': 2,
                'min_volume': 75,
                'max_units': 100
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

    def get_coins_with_open_orders(self):
        open_orders = self.exchange.get_open_orders()['result']
        if len(open_orders) == 0:
            return []
        else:
            return [x['Exchange'] for x in open_orders]

    def get_market_data(self):
        mkt_data = []
        for mkt in self.markets:
            logging.info(f'Getting market data for {mkt}')
            data = self.exchange.get_marketsummary(mkt)['result'][0]
            data['Change'] = calculate_change(data['Last'], data['Low'])
            mkt_data.append(data)
        return mkt_data

    def has_balance_to_buy(self):
        logging.info('checking if we have some balance to buy')
        q = self.exchange.get_balance(self.base_currency)
        # balance_adjustment to avoid INSUFFICIENT FUNDS MESSAGE
        balance_adjustment = 0.0005
        self.balance = q['result']['Available'] - balance_adjustment
        logging.debug(f'{self.balance}{self.base_currency} available')
        if self.balance >= self.min_order:
            return True
        else:
            return False

    def get_market_to_buy(self):
        self.update()
        mkt = [m for m in self.market_data if m[
            'BaseVolume'] >= self.min_volume]
        sorted_mkt = sorted(mkt, key=lambda x: x['BaseVolume'], reverse=True)
        while sorted_mkt[0]['MarketName'] in self.coins_with_open_orders:
            sorted_mkt.pop(0)
        return sorted_mkt[0]

    def buy(self, mkt):
        coin = mkt['MarketName']
        # get a price between ask and bid
        price = (mkt['Ask'] + mkt['Bid'])/2
        if self.balance > self.max_order:
            qnt = self.max_order/price
        else:
            qnt = self.balance/price
        if qnt > self.max_units:
            qnt = self.max_units
        if (qnt * price) < self.min_order:
            qnt = self.min_order/price
        logging.info(f'BUY {qnt} {coin} - price {price}, total {price * qnt}')
        order = self.exchange.buy_limit(coin, qnt, price)
        if order['success']:
            self.orders.append(order['result']['uuid'])
        else:
            logging.error(f'BUY FAIL - {order}')
        return(order)

    def sell(self):
        for order in self.orders:
            order_info = self.exchange.get_order(order)['result']
            if order_info['Closed']:
                coin = order_info['Exchange']
                qnt = order_info['Quantity']
                price = profit(order_info['PricePerUnit'], self.profit)
                sell_order = self.exchange.sell_limit(coin, qnt, price)
                self.orders.remove(order)
                logging.info(f'SELL {order} {sell_order}')

    def update(self):
        logging.info('Updating data')
        self.markets = self.get_markets()
        self.market_data = self.get_market_data()
        self.coins_with_open_orders = self.get_coins_with_open_orders()

    def do_trade(self):
        if self.has_balance_to_buy():
            self.buy(self.get_market_to_buy())
        if len(self.orders) > 0:
            self.sell()
        logging.info(f'Sleeping for {self.sleep_time} seconds')
        sleep(self.sleep_time)

    def run(self):
        logging.info('Starting Bot')
        while True:
            self.do_trade()
