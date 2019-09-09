#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pip3 install httplib2
# pip3 install openpyxl


import httplib2, urllib
import json
import openpyxl

class TKkt():
    regNumber      = '' #
    name           = '' #
    serialNumber   = '' #
    organizationId = '' #
    modelName      = '' #
    salesPointId   = '' #
    salesPointName = '' #
    fnSerialNumber = '' #
    endPay         = ''  #

class TSalesPoint():
    organizationId = '' # id Организации за которой закреплена данная точка продаж
    id             = '' # id Точки продажи
    name           = '' # Имя Точки продажи

class TOrganization():
    id             = '' # id организации в Контур
    inn            = '' # ИНН организации
    kpp            = '' # КПП организации
    shortName      = '' # Краткое наименование организации
    fullName       = '' # Полное наименование организации
    isBlocked      = '' # Заблокирована ли организация или нет
    creationDate   = '' #
    hasEvotorOffer = '' #

    SalesPoints = [] # Списка точек продаж организации
    Kkts = []

class TKontur():
    ofd_api_key  = '' # ключ интегратора
    SID          = '' #
    cookies      = {}
    cookieDomain = '' #
    endPoint     = '' # площадка
    mail         = '' # емаил авторизации
    passwd       = '' # пароль авторизации

    authStatusCode = '' # код статуса авторизации

    Organizations  = []

    def __init__(self):
        """Constructor"""
        pass

    def authenticate_by_pass(self):
        # Аутентификация/авторизация и получение SID-a (https://kontur-ofd-api.readthedocs.io/ru/latest/Auth/authenticate-by-pass.html)
        url_str             = 'https://api.kontur.ru/auth/authenticate-by-pass?login=' + self.mail  # урл авторизации
        h                   = httplib2.Http('.cache')
        (resp, content)     = h.request(uri=url_str, method='POST', body=self.passwd)
        self.authStatusCode = str(resp.status)

        if self.authStatusCode == '200':
            self.SID = content.decode("utf-8")
            self.SID = self.SID[8:]
            self.SID = self.SID[:-2]

            self.cookies = {'Cookie': 'ofd_api_key=' + self.ofd_api_key + ';auth.sid=' + self.SID}

    def get_organizations(self):
        # метод organizations (https://kontur-ofd-api.readthedocs.io/ru/latest/http/organizations.html)
        if self.authStatusCode == '200':
            url_str         = self.endPoint + 'v1/organizations'
            h               = httplib2.Http('.cache')
            (resp, content) = h.request(uri=url_str, method='GET', headers=self.cookies)

            # print (resp)
            #print (content.decode("utf-8"))

            if str(resp.status) == '200':
                json_obj = json.loads(content.decode("utf-8"))
                for item in json_obj:
                    Organization                = TOrganization()
                    Organization.id             = item ['id']
                    Organization.inn            = item ['inn']
                    Organization.kpp            = item ['kpp']
                    Organization.shortName      = item ['shortName']
                    Organization.fullName       = item ['fullName']
                    Organization.isBlocked      = item ['isBlocked']
                    Organization.creationDate   = item ['creationDate']
                    Organization.hasEvotorOffer = item ['hasEvotorOffer']
                    self.Organizations.append (Organization)

    def get_sales_point(self):
        # метод salespoints (недокументированный)
        # получение списка точек продаж организации
        for org in self.Organizations:
            url_str         = self.endPoint + 'v1/organizations/' + org.id + '/salesPoints'
            h               = httplib2.Http('.cache')
            (resp, content) = h.request(uri=url_str, method='GET', headers=self.cookies)

            if str(resp.status) == '200':
                json_obj = json.loads(content.decode("utf-8"))
                for item in json_obj:
                    SalesPoint                = TSalesPoint()
                    SalesPoint.organizationId = item['organizationId']
                    SalesPoint.id             = item['id']
                    SalesPoint.name           = item['name']

                    org.SalesPoints.append(SalesPoint)

    def get_cashboxes(self):
        # метод cashboxes (https://kontur-ofd-api.readthedocs.io/ru/latest/http/cashboxes.html)
        # получаем списки ККТ по всем организациям доступным пользователю
        for org in self.Organizations:
            url_str         = self.endPoint + 'v1/organizations/' + org.id + '/cashboxes'
            h               = httplib2.Http('.cache')
            (resp, content) = h.request(uri=url_str, method='GET', headers=self.cookies)

            if str(resp.status) == '200':
                json_obj = json.loads(content.decode("utf-8"))

                for item in json_obj:
                    Kkt                = TKkt()
                    Kkt.regNumber      = item['regNumber']
                    Kkt.name           = item['name']
                    Kkt.serialNumber   = item['serialNumber']
                    Kkt.organizationId = item['organizationId']
                    Kkt.modelName      = item['modelName']
                    Kkt.salesPointId   = item['salesPointPeriods'][0]['salesPointId'] # !!! поидеи надо в цикле дёргать
                    Kkt.fnSerialNumber = item['fnEntity']['serialNumber']

                    for sp in org.SalesPoints:
                        if Kkt.salesPointId == sp.id:
                            Kkt.salesPointName = sp.name
                            break

                    org.Kkts.append(Kkt)

    def get_cashboxes_xlsx(self):
        for org in self.Organizations:
            url_str = self.endPoint + 'v1/organizations/' + org.id + '/cashbox-connection/cashboxes'
            h = httplib2.Http('.cache')
            (resp, content) = h.request(uri=url_str, method='GET', headers=self.cookies)

            xlsx = 'log.xlsx'
            f = open(xlsx, 'wb') #
            f.write(content)
            f.close()

            wb = openpyxl.load_workbook(xlsx)
            ws = wb.worksheets[0]
            #xlsxWs = xlsxWb.active

            for i in range(2, ws.max_row+1):
                for kkt in org.Kkts:

                    if kkt.regNumber == str(ws.cell(row=i, column=2).value):
                        #print (ws.cell(row=i, column=4).value)
                        kkt.endPay = str(ws.cell(row=i, column=10).value)[13:]

                        #print (kkt.regNumber + ' - ' +kkt.endPay)
                        break

# --------------------------------------------------------------------------------------------------------------------

Kontur = TKontur()

#

Kontur.ofd_api_key  = '' # ключ для доступа личного кабинета через браузер
Kontur.SID          = ''
Kontur.cookieDomain = '.kontur.ru'
Kontur.endPoint     = 'https://ofd-api.kontur.ru/'
Kontur.mail         = ''
Kontur.passwd       = ''

#

Kontur.authenticate_by_pass()
#print (Kontur.SID)

#

Kontur.get_organizations()
#print (len(Kontur.Organizations))

#

Kontur.get_sales_point()

#

Kontur.get_cashboxes()

#

Kontur.get_cashboxes_xlsx()

#

# Вывод ККТ организации
#for org in Kontur.Organizations:
#    print (org.shortName)
#    for kkt in org.Kkts:
#        print ('  ' + kkt.salesPointName + ' - ('+kkt.regNumber +')')

# Вывод ККТ организации в разрезе точек продаж
for org in Kontur.Organizations:
    print (org.shortName)
    for sp in org.SalesPoints:
        print ('  '+sp.name)
        for kkt in org.Kkts:
            if sp.id == kkt.salesPointId:
                print ('    '+kkt.regNumber)
                print ('      ' + kkt.endPay)