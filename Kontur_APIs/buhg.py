#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import pymongo
from datetime import datetime

def delta_days(tstmp):
    # 22.11.2020 - now = result

    result = -1
    if len (tstmp) == 10:
        if tstmp[2] == '.' and tstmp[5] == '.':
            tstmp    = datetime(int(tstmp[6:10]), int(tstmp[3:5]), int(tstmp[0:2]))
            tstmpNow = datetime.now()
            delta    = tstmp - tstmpNow
            result   = int(delta.days)

    return result

conn   = pymongo.MongoClient('localhost', 27017)
db     = conn['TKontur']

dbOrgs = db['orgs']
dbSps  = db['sps']
dbKkts = db['kkts']

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
print ('Content-type: text/html\n\n')
form = cgi.FieldStorage()
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#print ('helllllooo')
#p1 = form.getfirst("p1", "val1")
#print (p1)


print ('<!DOCTYPE HTML>')
print ('<html>')
print ('    <head>')
print ('        <meta charset="utf-8">')
print ('        <title>Обработка данных форм</title>')
print ('    </head>')
print ('    <body>')

"""
print ('        <form action="/py/test.py" method="POST">')
print ('            <p>')
print ('                <select name="select">')
print ('                    <option name="n1" selected value="s1">Чебурашка</option>')
print ('                    <option name="n2" value="s2">Крокодил Гена</option>')
print ('                    <option name="n3" value="s3">Шапокляк</option>')
print ('                    <option name="n4" value="s4">Крыса Лариса</option>')
print ('                </select>')
print ('                <input type="submit" value="Отправить">')
print ('            </p>')
print ('        </form>')
"""

print ('<p><h3> Осталось дней до окончания услуги Контур ОФД </h3></p>')

print ('        <table border="1" cellpadding="5" cellspacing="0">')

print ('<tr>')
print ('<th>Организация</th>')
print ('<th>Точка продаж</th>')
print ('<th>Рег. №</th>')
print ('<th>Имя</th>')
print ('<th>Серийный №</th>')
print ('<th>Рег. № ФН</th>')
print ('<th>Статус</th>')
print ('<th>Осталось дней</th>')
print ('<th>Дата обновления данных</th>')
print ('</tr>')

for kkt in dbKkts.find():
    endPay = delta_days(kkt['endPay'])
    if endPay != -1:
        if endPay < 30:
            if kkt['state'] != 'Закрыт фискальный накопитель':
                print ('<tr>')

                org = dbOrgs.find_one({'id':kkt['organizationId']})      
                print ('<td>' + org['shortName'] + '</td>')

                sp = dbSps.find_one({'id': kkt['salesPointId']})
                print ('<td>' + sp['name'] + '</td>')

                print ('<td>' + kkt['regNumber'] + '</td>')
                print ('<td>' + kkt['name'] + '</td>')
                print ('<td>' + kkt['serialNumber'] + '</td>')
                print ('<td>' + kkt['fnSerialNumber'] + '</td>')
                print ('<td>' + kkt['state'] + '</td>')
                print ('<td bgcolor="#FDDAC5">' + str(endPay) + '</td>')
                print ('<td>' + kkt['addDate'] + '</td>')
                print ('</tr>')

print ('        </table>')
print ('    </body>')
print ('</html>')
