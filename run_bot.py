import yaml
from tradebot import TradeBot


with open('config.yaml') as f:
    cfg = yaml.safe_load(f.read())
bot = TradeBot(cfg['API_KEY'], cfg['API_SECRET'], **cfg['config'])


if __name__ == '__main__':
    bot.run()
