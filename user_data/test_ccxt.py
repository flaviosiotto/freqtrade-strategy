import ccxt

exchange = ccxt.binance()

ob = exchange.fetch_l2_order_book('BTC/USDT')

for x in exchange.has:
    print(x, exchange.has[x])

print(ob)
