from run_bot import bot

orders = bot.exchange.get_open_orders()['result']

for order in orders:
    mkt = order['Exchange']
    limit = order['Limit']
    bid = bot.exchange.get_marketsummary(mkt)['result'][0]['Bid']
    order['Diff'] = ((bid/limit) * 100) - 100

for order in sorted(orders, key=lambda x: x['Diff'], reverse=True):
    print(f"{order['Exchange']} {order['Diff']}")
