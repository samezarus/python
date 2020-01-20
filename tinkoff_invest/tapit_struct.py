#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
import json
import httplib2
import urllib
import cgi
from datetime import datetime, timedelta
from pytz import timezone
########################################################################################################################
########################################################################################################################
########################################################################################################################
def dtToUrlFormat(dtStr):
    # Функция для корректного форматирования ДатыВремя в URL

    result = str(dtStr).replace(':', '%3A')
    result = result.replace('+', '%2B')
    return result
########################################################################################################################
def url_get(url, headers):
    h      = httplib2.Http('.cache')
    (resp, content) = h.request(uri=url, method='GET', headers=headers)

    urlResult = {
        'resp'   : resp,
        'content': json.loads(content.decode("utf-8")),
        'status' : resp['status']
    }

    return urlResult
########################################################################################################################
def url_post(url, headers, params):
    header = {'Authorization': 'Bearer ' + token}
    h      = httplib2.Http('.cache')
    #return h.request(uri=url, method='POST', headers=header, body=urllib.parse.urlencode(params))

    #(resp, content) = h.request(uri=url, method='POST', headers=header, body=urllib.parse.urlencode(params))
    (resp, content) = h.request(uri=url, method='POST', headers=headers, body=params)

    urlResult = {
        'resp'   : resp,
        'content': json.loads(content.decode("utf-8")),
        'status' : resp['status']
    }
    return urlResult
########################################################################################################################
def web_prin_top(iterval):
    # iterval - интервал обновления страницы
    print('Content-type: text/html\n\n')
    webFormData = cgi.FieldStorage()
    print('<html>')
    print('<head>')
    print('<meta charset="utf-8">')
    if iterval > 0:
        print('<meta http-equiv="refresh" content="'+str(iterval)+'">')
    print('</head>')
    print('<body>')
########################################################################################################################
def web_prin_buttom():
    print('</body>')
    print('</html>')
########################################################################################################################
def get_figi_name_from_api(url, headers, figi):
    url       = url + '/market/search/by-figi?figi=' + figi
    urlResult = url_get(url, headers)

    if urlResult['status'] == '200':
        content = urlResult['content']
        if content['status'] == 'Ok':
            message = content['payload'].get('message')
            if message == None:
                result = content['payload']['name']
            else:
                result = message
    else:
        result = 'status: '+urlResult['status']

    return result
########################################################################################################################
def get_figi_name_from_mongo(figi, collection):
    result = collection.find({'figi': figi})

    if result.count() > 0:
        result = result[0]
        result = result.get('name')
        if result == None:
            result = 'Ключ name не найден в результате запроса'
    else:
        result = 'В БД отсутствует инфо. о ' + figi

    return result
########################################################################################################################
########################################################################################################################
########################################################################################################################
class TTinkoffApiTradePortfolio():
    #
    def __init__(self, params):
        self.params = params

        self.get_positions_from_api()
        self.get_currencies_from_api()
    #
    def clear_class_items(self):
        self.positions  = [] # список словарей инструментов в портфеле
        self.currencies = [] # список словарей валют в портфеле
    #
    def get_positions_from_api(self):
        # Получение самых актуальных данных об инструментах в портфеле через API
        self.clear_class_items()

        url = self.params['url'] + '/portfolio'

        urlResult = url_get(url, self.params['headers'])
        if urlResult['status'] == '200':
            content = urlResult['content']

            if content['status'] == 'Ok':
                message = content['payload'].get('message') # Если в 'payload' нет тела ошибки
                if message == None:
                    jpositions = content['payload'].get('positions')
                    self.get_positions(jpositions)
    #
    def get_positions(self, jpositions):
        for item in jpositions:
            position = self.create_position()

            key = 'figi'
            if item.get(key) != None:
                position[key] = item[key]

            key = 'ticker'
            if item.get(key) != None:
                position[key] = item[key]

            key = 'isin'
            if item.get(key) != None:
                position[key] = item[key]

            key = 'instrumentType'
            if item.get(key) != None:
                position[key] = item[key]

            key = 'balance'
            if item.get(key) != None:
                position[key] = item[key]

            key = 'lots'
            if item.get(key) != None:
                position[key] = item[key]

            key = 'expectedYield'
            if item.get(key) != None:
                position[key+'_currency'] = item[key]['currency']
                position[key+'_value']    = item[key]['value']

            key = 'averagePositionPrice'
            if item.get(key) != None:
                position[key + '_currency'] = item[key]['currency']
                position[key + '_value'] = item[key]['value']

            key = 'averagePositionPriceNoNkd'
            if item.get(key) != None:
                position[key + '_currency'] = item[key]['currency']
                position[key + '_value'] = item[key]['value']

            self.positions.append(position)
    #
    def create_position(self):
        position = {
            'figi'          : '',
            'ticker'        : '',
            'isin'          : '',
            'instrumentType': '',
            'balance'       : 0,
            'blocked'       : 0,
            'lots'          : 0,
            'expectedYield_currency': '',
            'expectedYield_value'   : 0,
            'averagePositionPrice_currency': '',
            'averagePositionPrice_value'   : 0,
            'averagePositionPriceNoNkd_currency': '',
            'averagePositionPriceNoNkd_value'   : 0
        }
        return position
    #
    def get_currencies_from_api(self):
        url = self.params['url'] + '/portfolio/currencies'
        urlResult = url_get(url, self.params['headers'])

        if urlResult['status'] == '200':
            content = urlResult['content']
            if content['status'] == 'Ok':
                message = content['payload'].get('message')  # Если в 'payload' нет тела ошибки
                if message == None:
                    jcurrencies = content['payload'].get('currencies')
                    for item in jcurrencies:
                        if item.get('blocked') == None:
                            item['blocked'] = 0
                        self.currencies.append(item)
    #
    def get_true_yield(self, balance, oneBayPrice, allExpectedYield, pc):
        # Функция расчитывает правдивый профит.
        # От показываемого профита отнимается комиссия покупки и продажи(если продавать "сейчас")

        # balance          - Количество доступных единиц в портфеле
        # oneBayPrice      - Средняя цена покупки единицы
        # allExpectedYield - Ожидаемая доходность всех единиц
        # pc               - процент коммисии

        oneBayCommission = (oneBayPrice / 100) * pc   # Средняя коммисия при покупке единицы
        allBayCommission = oneBayCommission * balance # Средняя коммисия при покупке всех единиц

        oneExpectedYield = allExpectedYield / balance  # Ожидаемая доходность единицы

        oneSalePrice = oneBayPrice + oneExpectedYield   # Средняя цена продажи единицы
        oneSaleCommission = (oneSalePrice / 100) * pc   # Средняя коммисия при продаже единицы
        allSaleCommission = oneSaleCommission * balance # Средняя коммисия при продаже всех единиц

        allTrueYield = allExpectedYield - allBayCommission - allSaleCommission  # Чистая доходность при продаже всех единиц
        oneTrueYield = allTrueYield / balance                                   # Чистая доходность при продаже единицы

        yieldResult = {
            'allTrueYield': allTrueYield,
            'oneTrueYield': oneTrueYield
        }
        return yieldResult
    #
    def web_print_portfolio(self, nameFl):
        web_prin_top(1)

        if len(self.positions) > 0:
            print('<table border="1" cellpadding="5" cellspacing="0">')

            print('<tr>')
            print('<td>' + 'Инструмент' + '</td>')
            print('<td>' + 'Количество' + '</td>')
            print('<td>' + 'Средняя <br> цена <br> покупки' + '</td>')
            print('<td>' + 'Грязная <br> прибыль <br> со <br> всего <br> количества' + '</td>')
            print('<td>' + 'Чистая <br> прибыль <br> со <br> всего <br> количества' + '</td>')
            print('<td>' + 'Чистая <br> прибыль <br> с <br> единицы' + '</td>')
            print('<td>' + 'FIGI' + '</td>')
            print('</tr>')

            for item in self.positions:
                balance          = item['balance']
                oneBayPrice      = item['averagePositionPrice_value']
                allExpectedYield = item['expectedYield_value']
                pc               = self.params['pc']
                yieldResult      = self.get_true_yield(balance, oneBayPrice, allExpectedYield, pc)

                allTrueYield = yieldResult['allTrueYield']
                oneTrueYield = yieldResult['oneTrueYield']

                clrG = '#d9f2d9'
                clrR = '#ffe6e6'

                if allTrueYield > 0:
                    bgClr = clrG
                else:
                    bgClr = clrR

                figi = item['figi']

                if nameFl == 0:
                    instrumentName = get_figi_name_from_api(self.params['url'], self.params['token'], figi)
                if nameFl == 1:
                    instrumentName = get_figi_name_from_mongo(figi, self.params['dbInstruments'])

                print('<tr>')
                print('<td bgcolor=' + bgClr + '>' + instrumentName + '</td>')
                print('<td bgcolor=' + bgClr + '>' + str(balance) + '</td>')
                print('<td bgcolor=' + bgClr + '>' + str(oneBayPrice) + '</td>')
                print('<td bgcolor=' + bgClr + '>' + str(allExpectedYield) + '</td>')
                print('<td bgcolor=' + bgClr + '>' + str(round(allTrueYield, 3)) + '</td>')
                print('<td bgcolor=' + bgClr + '>' + str(round(oneTrueYield, 3)) + '</td>')
                print('<td bgcolor=' + bgClr + '>' + figi + '</td>')
                print('</tr>')

            print('</table>')

        print('<br>')

        if len(self.currencies) > 0:
            print('<table border="1" cellpadding="5" cellspacing="0">')

            print('<tr>')
            print('<td>' + 'Валюта' '</td>')
            print('<td>' + 'Количество' + '</td>')
            print('<td>' + 'Заблокировано' + '</td>')
            print('<td>' + 'Свободно' + '</td>')
            print('</tr>')

            for item in self.currencies:
                print('<tr>')
                print('<td>' + item['currency'] + '</td>')
                print('<td>' + str(item['balance']) + '</td>')
                print('<td>' + str(item['blocked']) + '</td>')
                print('<td>' + str(round(item['balance'] - item['blocked'], 3)) + '</td>')
                print('</tr>')

            print('</table>')

        web_prin_buttom()
########################################################################################################################
class TTinkoffApiTradeOrders():
    #
    def __init__(self, params):
        self.params = params

        self.get_from_api()
    #
    def clear_class_items(self):
        self.items  = [] # список словарей
    #
    def get_from_api(self):
        self.clear_class_items()

        url = self.params['url'] + '/orders'

        urlResult = url_get(url, self.params['headers'])

        if urlResult['status'] == '200':
            content = urlResult['content']

            if content['status'] == 'Ok':
                if content.get('payload') != None:
                    jorders = content['payload']
                    if len(jorders) > 0:
                        for item in jorders:
                            message = item .get('message')
                            if message == None:
                                self.items.append(item)
    #
    def web_print_orders(self):
        pass
        #for item in self.
    #
    def set_orders(self, figi, lots, price):
        orderParams = '{"lots": ' + str(lots) + ', "operation": "Buy", "price": ' + str(price) + '}'
        url         = self.params['url'] + '/orders/limit-order?figi=' + figi
        urlResult   = url_post(url, self.params['headers'], orderParams)

        if urlResult['status'] == '200':
            result = urlResult['content']['status']
        else:
            result = 'status code: ' + urlResult['status']

        return result
    #
########################################################################################################################
class TTinkoffApiTradeOperations():
    #
    def __init__(self, params):
        self.params = params

        self.clear_class_items()
    #
    def clear_class_items(self):
        self.items = []  # список словарей
    #
    def get_operations_by_figi_from_api(self, figi, fromDate, toDate):
        # Получения операций по figi в промежутке дат

        url = self.params['url'] + '/operations?from=' + fromDate + '&to=' + toDate + '&figi=' + figi

        urlResult = url_get(url, self.params['headers'])

        if urlResult['status'] == '200':
            content = urlResult['content']

            if content['status'] == 'Ok':
                if content.get('payload') != None:
                    content = content['payload']

                    if content.get('operations') != None:
                        content = content['operations']

                        if len(content) > 0:
                            for item in content:
                                self.items.append(item)
    #
    def get_portfolio_operations_from_api(self, fromDate, toDate):
        # Получение операций по повсем инструментам в портфеле в промежутке между датами

        self.items = []

        portfolio = TTinkoffApiTradePortfolio(self.params)
        if len(portfolio.positions) > 0:
            for item in portfolio.positions:
                self.get_operations_by_figi_from_api(item['figi'], fromDate, toDate)
    #
    def get_all_portfolio_operations_from_api(self):
        # Получение всех операций по всем инструментам в портфеле за всё время

        now      = datetime.now(tz=timezone('Europe/Moscow'))
        fromDate = dtToUrlFormat('1970-12-12T00:00:00+03:00')
        toDate   = dtToUrlFormat(now.isoformat())

        self.get_portfolio_operations_from_api(fromDate, toDate)
    #
########################################################################################################################
class TTinkoffApiTradeСandles():
    #
    def __init__(self, params):
        self.params = params
        self.items  = []  # список словарей
    #
########################################################################################################################
class TTinkoffApiTradeOrderbook():
    #
    def __init__(self, params):
        self.params = params

        self.clear_class_items()

    #
    def clear_class_items(self):
        self.tradeStatus       = ''  #
        self.minPriceIncrement = 0.0 #
        self.lastPrice         = 0.0 #
        self.closePrice        = 0.0 #
        self.limitUp           = 0.0 #
        self.limitDown         = 0.0 #
        self.bids              = []  # список словарей покупок
        self.asks              = []  # список словарей продаж
    #
    def get_orderbook_from_api(self, figi, depth):
        url = self.params['url'] + '/market/orderbook?figi='+figi+'&depth='+str(depth)

        urlResult = url_get(url, self.params['headers'])

        if urlResult['status'] == '200':
            content = urlResult['content']

            if content['status'] == 'Ok':
                if content.get('payload') != None:
                    content = content['payload']

                    #print(content)

                    self.tradeStatus       = content['tradeStatus']
                    self.minPriceIncrement = content['minPriceIncrement']
                    self.lastPrice         = content['lastPrice']
                    self.closePrice        = content['closePrice']
                    self.limitUp           = content['limitUp']
                    self.limitDown         = content['limitDown']
                    self.bids              = content['bids']
                    self.asks              = content['asks']
    #

########################################################################################################################
class TTemplate():
    #
    def __init__(self, params):
        self.params = params
        self.items  = []  # список словарей
    #