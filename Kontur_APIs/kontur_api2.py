#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pip3 install httplib2
# pip3 install openpyxl


import httplib2, urllib
import json
import openpyxl

class TKkt():
    regNumber      = '' # Регистрациооный номер
    name           = '' # имя ККТ
    serialNumber   = '' # Заводской номер ККТ
    organizationId = '' # id организации
    modelName      = '' # Название модели
    salesPointId   = '' # id точки продаж
    fnSerialNumber = '' # Заводской номер ФН
    ffd            = '' # из xlsx "ФФД"
    state          = '' # из xlsx "Состояние ККТ"
    lastDoc        = '' # из xlsx "Последний документ"
    lastDocDate    = '' # из xlsx "Дата последнего документа"
    endPay         = '' # из xlsx "Оплата"
    ofd            = '' # из xlsx "ОФД"
    fnChangeDate   = '' # из xlsx "Срок замены ФН"

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
    SalesPoints    = []  # Списка точек продаж организации
    Kkts           = []

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

            if str(resp.status) == '200':
                json_obj = json.loads(content.decode("utf-8"))
                for item in json_obj:
                    Organization                = TOrganization()
                    Organization.id             = item ['id']
                    Organization.inn            = item ['inn']
                    #Organization.kpp            = item ['kpp'] # нет у ИП
                    Organization.shortName      = item ['shortName']
                    Organization.fullName       = item ['fullName']
                    Organization.isBlocked      = item ['isBlocked']
                    #Organization.creationDate   = item ['creationDate'] # нет у пустой организации
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

                    self.SalesPoints.append(SalesPoint)

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

                    self.Kkts.append(Kkt)

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
                for kkt in self.Kkts:
                    if kkt.regNumber == str(ws.cell(row=i, column=2).value):
                        kkt.ffd          = str(ws.cell(row=i, column=6).value)
                        kkt.state        = str(ws.cell(row=i, column=7).value)
                        kkt.lastDoc      = str(ws.cell(row=i, column=8).value)
                        kkt.lastDocDate  = str(ws.cell(row=i, column=9).value)
                        kkt.endPay       = str(ws.cell(row=i, column=10).value)
                        kkt.ofd          = str(ws.cell(row=i, column=14).value)
                        kkt.fnChangeDate = str(ws.cell(row=i, column=15).value)

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

f = open('log.html', 'w')
f.write('<html>')
f.write('<body>')

for org in Kontur.Organizations:
    print (org.shortName)
    f.write('<br>')
    f.write('<p><font color="#59b300"><h1>'+org.shortName+'</h1></font></p>')
    for sp in Kontur.SalesPoints:
        if sp.organizationId == org.id:
            print ('  '+sp.name)
            f.write('<h3>' + sp.name + '</h3>')

            f.write('<table border="1" cellpadding="5" cellspacing="0">')
            f.write('<tr>')
            f.write('<th>Заводской №</th>')
            f.write('<th>Регистрационный №</th>')
            f.write('<th>Заводской № ФН</th>')
            f.write('<th>ФФД</th>')
            f.write('<th>Состояние ККТ</th>')
            f.write('<th>Последний документ</th>')
            f.write('<th>Дата последнего документа</th>')
            f.write('<th>Оплата</th>')
            f.write('<th>ОФД</th>')
            f.write('<th>Срок замены ФН</th>')
            f.write('</tr>')

            for kkt in Kontur.Kkts:
                if (kkt.organizationId == org.id) and (kkt.salesPointId == sp.id):
                    f.write('<tr>')
                    print ('    ' + kkt.regNumber)
                    print ('    ' + kkt.endPay)
                    f.write('<td>' + kkt.serialNumber + '</td>')
                    f.write('<td>' + kkt.regNumber + '</td>')
                    f.write('<td>' + kkt.fnSerialNumber + '</td>')

                    f.write('<td>' + kkt.ffd + '</td>')
                    f.write('<td>' + kkt.state + '</td>')
                    f.write('<td>' + kkt.lastDoc  + '</td>')
                    f.write('<td>' + kkt.lastDocDate + '</td>')
                    f.write('<td>' + kkt.endPay + '</td>')
                    f.write('<td>' + kkt.ofd  + '</td>')
                    f.write('<td>' + kkt.fnChangeDate + '</td>')
                    f.write('</tr>')

            f.write('</table>')

f.write('</body>')
f.write('</html>')
f.close()
