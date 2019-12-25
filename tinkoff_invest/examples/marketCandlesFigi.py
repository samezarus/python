#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tapit

import json

from datetime import datetime, timedelta
from pytz import timezone

tnkf = tapit.TTinkoffApiTrade('conf.txt')

# curl -X GET "https://api-invest.tinkoff.ru/openapi/market/candles?figi=BBG000CL9VN6&from=2019-12-20T09%3A28%3A59.482662%2B03%3A00&to=2019-12-24T09%3A28%3A59.482662%2B03%3A00&interval=day" -H "accept: application/json" -H "Authorization: Bearer <token>"

now   = datetime.now(tz=timezone('Europe/Moscow'))
unNow = now - timedelta(days=100)

figi = 'BBG000BMX289' # Coca cola
fromDate = tapit.dtToUrlFormat(unNow.isoformat())
toDate = tapit.dtToUrlFormat(now.isoformat())

url = '/market/candles?figi='+figi+'&from='+fromDate+'&to='+toDate+'&interval=day'

res = tnkf.getData(url)
#print (res.resp)
print (res.content)

marketCandlesFigi = res.content

for item in marketCandlesFigi['payload']['candles']:
    print (item)





