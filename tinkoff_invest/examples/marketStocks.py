#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# доступные инструменты(акции/облигации)

import tapit

import json

tnkf = tapit.TTinkoffApiTrade('conf.txt')

marketStocks = tnkf.getData('/market/stocks').content

print (marketStocks)

for item in marketStocks['payload']['instruments'] :
    # print(item) # Все параметры инструмента
    print('Имя: ' + item['name'])
    print('figi: ' + item['figi'])
    print('---------------------')