#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pip3 install httplib2
# pip3 install openpyxl
# pip3 install pymongo
# pip3 install pymysql

import httplib2, urllib
import json
import openpyxl
import pymongo
import pymysql
from datetime import datetime

class TKkt():
    # из json-a
    regNumber      = '' # Регистрациооный номер
    name           = '' # имя ККТ
    serialNumber   = '' # Заводской номер ККТ
    organizationId = '' # id организации
    modelName      = '' # Название модели
    salesPointId   = '' # id точки продаж
    fnSerialNumber = '' # Заводской номер ФН
    # из xlsx "Список касс в Excel"
    ffd          = '' # "ФФД"
    state        = '' # "Состояние ККТ"
    lastDoc      = '' # "Последний документ"
    lastDocDate  = '' # "Дата последнего документа"
    endPay       = '' # "Оплата" (Срок окончания оплаты ОФД)
    ofd          = '' # "ОФД"
    fnChangeDate = '' # "Срок замены ФН"
    # из эксельки Райгородского
    firmware = '' # Версия прошивки ККТ
    mac      = '' # MAC - АДРЕС
    memo     = '' # Примечание
    # из УКМ-а
    ukmName = '' # имя в УКМ сервере
    #
    addDate = '' # Дата создания/обновления записи

class TSalesPoint():
    organizationId = '' # id Организации за которой закреплена данная точка продаж
    id             = '' # id Точки продажи
    name           = '' # Имя Точки продажи
    #
    addDate = '' # Дата создания/обновления записи

class TOrganization():
    id             = '' # id организации в Контур
    inn            = '' # ИНН организации
    kpp            = '' # КПП организации
    shortName      = '' # Краткое наименование организации
    fullName       = '' # Полное наименование организации
    isBlocked      = '' # Заблокирована ли организация или нет
    creationDate   = '' #
    hasEvotorOffer = '' #
    #
    addDate = ''  # Дата создания/обновления записи

class TKontur():
    ofd_api_key  = '' # ключ интегратора
    SID          = '' #
    cookies      = {}
    cookieDomain = '' #
    endPoint     = '' # площадка
    mail         = '' # емаил авторизации
    passwd       = '' # пароль авторизации

    authStatusCode = '' # код статуса авторизации

    Organizations = [] # Список организаций
    SalesPoints   = [] # Списка точек продаж организации
    Kkts          = [] # Список ККТ

    sgoServer   = ''
    sgoUser     = ''
    sgoPassword = ''
    sgoDb       = ''

    lastError = ''

    addonXlsxFile = '' # экселька Райгородского

    def __init__(self):
        """Constructor"""
        pass

    def end_pay_format(self, s):
        # "28.07.2019 - 28.08.2020" to "28.08.2020"
        result = s

        if s[2] == '.' and s[5] == '.' and s[11] == '-' and s[15] == '.' and s[18] == '.':
            result = s[13:23]

        return result

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
        else:
            self.lastError = 'Не могу авторизоваться'

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
                    Organization.addDate = datetime.now()

                    self.Organizations.append (Organization)
            else:
                self.lastError = 'Не могу получить список организаций'

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
                    SalesPoint.addDate = datetime.now()

                    self.SalesPoints.append(SalesPoint)
            else:
                self.lastError = 'Не могу получить список точек продаж у ' + org.shortName

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
                    Kkt.addDate = datetime.now()

                    self.Kkts.append(Kkt)
            else:
                self.lastError = 'Не могу получить список ККТ у ' + org.shortName

    def get_cashboxes_xlsx(self):
        for org in self.Organizations:
            url_str = self.endPoint + 'v1/organizations/' + org.id + '/cashbox-connection/cashboxes'
            h = httplib2.Http('.cache')
            (resp, content) = h.request(uri=url_str, method='GET', headers=self.cookies)

            if str(resp.status) == '200':
                xlsx = 'log.xlsx'
                f = open(xlsx, 'wb') #
                f.write(content)
                f.close()

                wb = openpyxl.load_workbook(xlsx)
                ws = wb.worksheets[0]

                for i in range(2, ws.max_row+1):
                    for kkt in self.Kkts:
                        if kkt.serialNumber == str(ws.cell(row=i, column=1).value):
                            kkt.ffd          = str(ws.cell(row=i, column=6).value)
                            kkt.state        = str(ws.cell(row=i, column=7).value)
                            kkt.lastDoc      = str(ws.cell(row=i, column=8).value)
                            kkt.lastDocDate  = str(ws.cell(row=i, column=9).value)
                            kkt.endPay       = self.end_pay_format(str(ws.cell(row=i, column=10).value))
                            kkt.ofd          = str(ws.cell(row=i, column=14).value)
                            kkt.fnChangeDate = str(ws.cell(row=i, column=15).value)

                            break
            else:
                self.lastError = 'Не могу получить файл эксель с доп. инф. по ККТ у ' + org.shortName

    def addon_xlsx(self):
        wb = openpyxl.load_workbook(self.addonXlsxFile)
        ws = wb.worksheets[0]

        for i in range(2, ws.max_row + 1):
            for kkt in self.Kkts:
                if kkt.serialNumber == str(ws.cell(row=i, column=10).value):
                    kkt.firmware = str(ws.cell(row=i, column=13).value)
                    kkt.mac      = str(ws.cell(row=i, column=15).value)
                    kkt.memo     = str(ws.cell(row=i, column=19).value)

                    break

    def org_to_mongo(self):
        conn           = pymongo.MongoClient('localhost', 27017)
        db             = conn['TKontur']
        dbOrgs = db['orgs']

        for org in self.Organizations:
            doc = {"id": str(org.id),
                   "inn": str(org.inn),
                   "kpp": str(org.kpp),
                   "shortName": str(org.shortName),
                   "fullName": str(org.fullName),
                   "isBlocked": str(org.isBlocked),
                   "creationDate": str(org.creationDate),
                   "hasEvotorOffer": str(org.hasEvotorOffer),
                   "addDate": str(org.addDate),
                   }

            if dbOrgs.find({"id" : str(org.id)}).count() == 0:
                dbOrgs.save(doc)
            else:
                dbOrgs.update({"id": str(org.id)}, doc)

    def sp_to_mongo(self):
        conn           = pymongo.MongoClient('localhost', 27017)
        db             = conn['TKontur']
        dbSps = db['sps']

        for sp in self.SalesPoints:
            doc = {"organizationId": str(sp.organizationId),
                   "id": str(sp.id),
                   "name": str(sp.name),
                   "addDate": str(sp.addDate),
                   }

            if dbSps.find({"id": str(sp.id)}).count() == 0:
                dbSps.save(doc)
            else:
                dbSps.update({"id": str(sp.id)}, doc)

    def kkt_to_mongo(self):
        conn           = pymongo.MongoClient('localhost', 27017)
        db             = conn['TKontur']
        dbKkts = db['kkts']

        for kkt in self.Kkts:
            doc = {"regNumber": str(kkt.regNumber),
                   "name": str(kkt.name),
                   "serialNumber": str(kkt.serialNumber),
                   "organizationId": str(kkt.organizationId),
                   "modelName": str(kkt.modelName),
                   "salesPointId": str(kkt.salesPointId),
                   "fnSerialNumber": str(kkt.fnSerialNumber),
                   "ffd": str(kkt.ffd),
                   "state": str(kkt.state),
                   "lastDoc": str(kkt.lastDoc),
                   "lastDocDate": str(kkt.lastDocDate),
                   "endPay": str(kkt.endPay),
                   "ofd": str(kkt.ofd),
                   "fnChangeDate": str(kkt.fnChangeDate),
                   "firmware": str(kkt.firmware),
                   "mac": str(kkt.mac),
                   "memo": str(kkt.memo),
                   "ukmName": str(kkt.ukmName),
                   "addDate": str(kkt.addDate),
                   }

            if dbKkts.find({"serialNumber": str(kkt.serialNumber)}).count() == 0:
                dbKkts.save(doc)
            else:
                dbKkts.update({"serialNumber": str(kkt.serialNumber)}, doc)

    def from_sgo(self):
        #
        connection = pymysql.connect(host=self.sgoServer,
                                     user=self.sgoUser,
                                     password=self.sgoPassword,
                                     db=self.sgoDb,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor
                                     )
        try:
            conn   = pymongo.MongoClient('localhost', 27017)
            db     = conn['TKontur']
            dbUkms = db['ukms']

            with connection.cursor() as cursor:
                # trm_in_pos (name)
                # trm_out_shift_close(cash_id)
                sql = 'SELECT DISTINCT trm_out_shift_close.kkm_serial_number, trm_in_pos.name from trm_out_shift_close, trm_in_pos WHERE trm_out_shift_close.cash_id = trm_in_pos.cash_id'
                cursor.execute(sql)
                for row in cursor:
                    for kkt in self.Kkts:
                        if row['kkm_serial_number'] ==  kkt.serialNumber:
                            kkt.ukmName = row['name']
                            break
        finally:
            connection.close()
# --------------------------------------------------------------------------------------------------------------------

Kontur = TKontur()

#

Kontur.ofd_api_key   = '' # ключ для доступа личного кабинета через браузер
Kontur.SID           = ''
Kontur.cookieDomain  = '.kontur.ru'
Kontur.endPoint      = 'https://ofd-api.kontur.ru/'
Kontur.mail          = ''
Kontur.passwd        = ''
Kontur.sgoServer     = ''
Kontur.sgoUser       = ''
Kontur.sgoPassword   = ''
Kontur.sgoDb         = ''
Kontur.addonXlsxFile = 'addon.xlsx'

#

Kontur.authenticate_by_pass()
#print (Kontur.SID)
print (Kontur.lastError)
#

Kontur.get_organizations()
#print (len(Kontur.Organizations))
print (Kontur.lastError)
#

Kontur.get_sales_point()
print (Kontur.lastError)
#

Kontur.get_cashboxes()
print (Kontur.lastError)
#

Kontur.get_cashboxes_xlsx()
print (Kontur.lastError)
#

Kontur.addon_xlsx()

#

Kontur.from_sgo()

#

Kontur.org_to_mongo()
Kontur.sp_to_mongo()
Kontur.kkt_to_mongo()

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
            f.write('<th>Название ККТ</th>')
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
                    f.write('<td>' + kkt.name + '</td>')
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

