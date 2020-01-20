#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import httplib2
import urllib
import json
from datetime import datetime, timedelta
from pytz import timezone
import pymongo
import cgi
#
from tapit_struct import dtToUrlFormat
from tapit_struct import url_get
from tapit_struct import web_prin_top
from tapit_struct import web_prin_buttom
from tapit_struct import TTinkoffApiTradePortfolio
from tapit_struct import TTinkoffApiTradeOrders
from tapit_struct import TTinkoffApiTradeOperations
from tapit_struct import TTinkoffApiTradeOrderbook

#
class httpResult():
    resp    = 'nil'
    content = 'nil'
#
class TTinkoffApiTrade():
    def __init__(self):
        self.get_conf()
    #
    def get_conf(self):
        confFile     = open('conf.txt', 'r')
        confParams   = json.load(confFile)
        self.apiURL  = 'https://api-invest.tinkoff.ru/openapi'
        self.token   = confParams['token']                # Токен для торгов
        self.headers = {'Authorization': 'Bearer ' + self.token}
        self.pc      = confParams['percentageCommission'] # Базовая комиссия при операциях

        dbHost = confParams['db']['host']
        dbPort = confParams['db']['port']
        dbName = confParams['db']['name']

        conn = pymongo.MongoClient(dbHost, dbPort)
        db   = conn[dbName]

        self.dbInstruments = db['dbInstruments'] # /market/stocks
        self.dbOperations  = db['dbOperations']   # /operations
    #
    def get_data(self, qString):
        result = httpResult()

        if self.token != '':
            header          = {'Authorization': 'Bearer ' + self.token}
            url_str         = self.apiURL + qString
            h               = httplib2.Http('.cache')
            (resp, content) = h.request(uri=url_str, method='GET', headers=header)

            result.resp    = resp
            result.content = json.loads(content.decode("utf-8"))
        else:
            print ('Ключ пуст')

        return result
    #
    def market_search_by_figi_from_api(self, figi):
        url     = '/market/search/by-figi?figi=' + figi
        content = self.get_data(url).content
        return content['payload']
    #
    def market_search_by_figi_from_mongo(self, figi):
        #result = ''

        result = self.dbInstruments.find({'figi' : figi})

        return result
    #
    def instruments_to_mongo(self):
        # Вызывается только для первого наполнения БД или для обновления всех данных
        self.dbInstruments.remove()

        self.market_stocks_to_mongo()
        self.market_bonds_to_mongo()
        self.market_etfs_to_mongo()
        self.market_currencies_to_mongo()
    #
    def market_stocks_to_mongo(self):
        # Получение списка акций
        url     = '/market/stocks'
        content = self.get_data(url).content

        for item in content['payload']['instruments']:
            self.dbInstruments.save(item)
    #
    def market_bonds_to_mongo(self):
        # Получение списка облигаций
        url     = '/market/bonds'
        content = self.get_data(url).content

        for item in content['payload']['instruments']:
            self.dbInstruments.save(item)
    #
    def market_etfs_to_mongo(self):
        # Получение списка ETF
        url     = '/market/etfs'
        content = self.get_data(url).content

        for item in content['payload']['instruments']:
            self.dbInstruments.save(item)
    #
    def market_currencies_to_mongo(self):
        # Получение списка валютных пар
        url     = '/market/currencies'
        content = self.get_data(url).content

        for item in content['payload']['instruments']:
            self.dbInstruments.save(item)
    #
    def operations_to_mongo(self, fromDate, toDate, figi):
        url     = '/operations?from=' + fromDate + '&to=' + toDate + '&figi=' + figi
        content = self.get_data(url).content

        for item in content['payload']['operations']:
            id            = item['id']
            operationType = item['operationType']

            findResult = self.dbOperations.find({'id':id})

            if findResult.count() == 0 and (operationType == 'Buy' or operationType == 'Sell'):
                self.dbOperations.save(item)
                print(item)
    #
    def current_operations_to_mongo(self):
        # Получение операций по текущим инструментам и валютам в портфеле
        url     = '/portfolio'
        content = self.get_data(url).content

        now = datetime.now(tz=timezone('Europe/Moscow'))
        fromDate = dtToUrlFormat('1970-12-12T00:00:00+03:00')  # 2019-12-24T09:28:59.482662+03:00
        toDate = dtToUrlFormat(now.isoformat())

        for item in content['payload']['positions']:
            #print(item)
            print(self.operations_to_mongo(fromDate, toDate, item['figi']))
    #
    def print_all_current_operations(self):
        now = datetime.now(tz=timezone('Europe/Moscow'))
        fromDate = dtToUrlFormat('1970-12-12T00:00:00+03:00')  # 2019-12-24T09:28:59.482662+03:00
        toDate = dtToUrlFormat(now.isoformat())

        self.web_prin_top()

        url = '/portfolio'
        content = self.get_data(url).content

        for item in content['payload']['positions']:
            #print(str(item)+'<br>')
            # instrumentName = self.market_search_by_figi_from_api(item['figi'])['name']
            instrumentName = self.market_search_by_figi_from_mongo(item['figi'])[0]['name']
            print('<h3>' + instrumentName + '<br>' + '</h3>')

            url = '/operations?from=' + fromDate + '&to=' + toDate + '&figi=' + item['figi']
            content2 = self.get_data(url).content

            print('<table border="1" cellpadding="5" cellspacing="0">')

            for item2 in content2['payload']['operations']:
                if item2['operationType'] == 'Buy':
                    print('<tr>')
                    #print('<td>'+str(item2)+'</td>')
                    print('<td>' + str(item2['operationType']) + '</td>')
                    print('<td>' + str(item2['date']) + '</td>')
                    print('<td>' + str(item2['isMarginCall']) + '</td>')
                    print('<td>' + str(item2['instrumentType']) + '</td>')
                    print('<td>' + str(item2['quantity']) + '</td>')
                    print('<td>' + str(item2['price']) + '</td>')
                    print('<td>' + str(item2['payment']) + '</td>')
                    print('<td>' + str(item2['commission']['value']) + '</td>')

                    finalPriceAll = item2['payment'] + item2['commission']['value']
                    print('<td bgcolor="#ffcccc">' + str(finalPriceAll) + '</td>')
                    finalPriceOne = finalPriceAll / item2['quantity']
                    print('<td bgcolor="#ffc266">' + str(finalPriceOne) + '</td>')

                    print('<td>' + str(item2['status']) + '</td>')
                    print('</tr>')

            print('</table>')

        self.web_prin_buttom()
    #
    def orders_manager(self):
        params = {
                    'token'  : self.token,
                    'url'    : self.apiURL,
                    'headers': self.headers
        }

        return TTinkoffApiTradeOrders(params)
    #
    def portfolio_manager(self):
        params = {
            'token'        : self.token,
            'url'          : self.apiURL,
            'headers'      : self.headers,
            'pc'           : self.pc,
            'dbInstruments': self.dbInstruments
        }

        return TTinkoffApiTradePortfolio(params)
    #
    def operations_manager(self):
        params = {
            'token'  : self.token,
            'url'    : self.apiURL,
            'headers': self.headers
        }

        return TTinkoffApiTradeOperations(params)
    #
    def orderbook_manager(self):
        params = {
            'token'  : self.token,
            'url'    : self.apiURL,
            'headers': self.headers
        }

        return TTinkoffApiTradeOrderbook(params)
    #
