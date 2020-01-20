#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tapit

import json

from datetime import datetime, timedelta
from pytz import timezone
from tapit_struct import TTinkoffApiTradePortfolio

tnkf = tapit.TTinkoffApiTrade()

#print (tnkf.get_data('/portfolio').content)
#print (tnkf.get_data('/portfolio/currencies').content)
#print (tnkf.get_data('/market/bonds').content)
#print (tnkf.get_data('/market/currencies').content)
#print (tnkf.get_data('/market/etfs').content)
#print (tnkf.get_data('/market/stocks').content)
#print (tnkf.get_data('/orders').content)

# curl -X GET "https://api-invest.tinkoff.ru/openapi/market/candles?figi=BBG000CL9VN6&from=2019-12-20T09%3A28%3A59.482662%2B03%3A00&to=2019-12-24T09%3A28%3A59.482662%2B03%3A00&interval=day" -H "accept: application/json" -H "Authorization: Bearer <token>"

now   = datetime.now(tz=timezone('Europe/Moscow'))
unNow = now - timedelta(days=100)

#figi = 'BBG000BMX289' # Coca cola
figi = 'BBG0013HGFT4' # US $

fromDate = tapit.dtToUrlFormat(unNow.isoformat()) # 2019-12-24T09:28:59.482662+03:00
toDate = tapit.dtToUrlFormat(now.isoformat())

url = '/operations?from=' + fromDate + '&to=' + toDate + '&figi=' + figi

#res = tnkf.get_data(url)
#print (res.resp)
#print (res.content)

#for item in res.content['payload']['operations']:
#    print(item)

############################

#tnkf.instruments_to_mongo() # Обновляем список инструментов

#tnkf.operations_to_mongo(fromDate, toDate,figi) #

#tnkf.current_operations_to_mongo()


#tnkf.web_print_portfolio(1)
#tnkf.web_print_portfolio_compact(1)

# BBG000FJ0RK9 - LG Display

#orders = tnkf.orders_manager()

#for item in orders.items:
#    print(item)

#print(orders.items)


figi = 'BBG006L8G4H1' # Yandex
#params = """{"lots": 1, "operation": "Buy", "price": 6}"""
#params = '{"lots": 1, "operation": "Buy", "price": 6}'
#print (params)

#print(orders.set_orders(figi, 1, 6))

#operations = tnkf.operations_manager()
#operations.get_operations_by_figi_from_api(figi, fromDate, toDate)
#print(operations.items)
#operations.get_all_portfolio_operations_from_api()
#for item in operations.items:
#    print(item)

orderbook = tnkf.orderbook_manager()
while True:
    orderbook.get_orderbook_from_api(figi, 20)

    bids = orderbook.bids
    asks = orderbook.asks

    bidsSumm = 0
    for item in bids:
        bidsSumm += item['quantity']

    asksSumm = 0
    for item in asks:
        asksSumm += item['quantity']

    print('сумма покупокок: '+ str(bidsSumm))
    print('сумма продаж: '+ str(asksSumm))