#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tapit

import json

from datetime import datetime, timedelta
from pytz import timezone

tnkf = tapit.TTinkoffApiTrade('conf.txt')

url = '/portfolio'

res = tnkf.getData(url)
#print (res.resp)
print (res.content)

portfolio = res.content

for item in portfolio['payload']['positions']:
    print (item)



