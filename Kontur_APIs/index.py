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

for org in dbOrgs.find():
    if org['isBlocked'] == 'False':
        spList = dbSps.find({"organizationId": org['id']})

        if spList.count() > 0:
            print ('<p><font color="#59b300"><h3>'+org['shortName']+'</h3></font></p>')

            for sp in spList:
                if sp['organizationId'] == org['id']:
                    kktList = dbKkts.find({"salesPointId": sp['id']})
                    if kktList.count() > 0:
                        print ('<h4>'+sp['name']+'</h4>')

                        print ('<table border="1" cellpadding="5" cellspacing="0">')

                        print ('<tr>')

                        print ('<th>Рег. №</th>')
                        print ('<th>Имя (из ОФД)</th>')
                        print ('<th>Имя (из СГО)</th>')
                        print ('<th>Серийный №</th>')
                        print ('<th>Модель</th>')
                        print ('<th>Серийный № ФН</th>')
                        print ('<th>ФФД</th>')
                        print ('<th>Статус</th>')
                        print ('<th>Последний документ</th>')
                        print ('<th>Дата последненго документа</th>')
                        print ('<th>Оплата</th>')
                        print ('<th>тип ОФД</th>')
                        print ('<th>Дата замены ФН</th>')
                        print ('<th>Версия ПО</th>')
                        print ('<th>МАС-адрес</th>')
                        print ('<th>Заметка</th>')
                        print ('<th>Дата записи</th>')

                        print ('</tr>')

                        for kkt in kktList:
                            if kkt['state'] != 'Закрыт фискальный накопитель':
                                print ('<tr>')
                                print ('<td>' + kkt['regNumber'] + '</td>')
                                print ('<td>' + kkt['name'] + '</td>')
                                print ('<td>' + kkt['ukmName'] + '</td>')
                                print ('<td>' + kkt['serialNumber'] + '</td>')
                                #print ('<td>' + kkt['organizationId'] + '</td>')
                                print ('<td>' + kkt['modelName'] + '</td>')
                                #print ('<td>' + kkt['salesPointId'] + '</td>')
                                print ('<td>' + kkt['fnSerialNumber'] + '</td>')
                                print ('<td>' + kkt['ffd'] + '</td>')
                                print ('<td>' + kkt['state'] + '</td>')
                                print ('<td>' + kkt['lastDoc'] + '</td>')
                                print ('<td>' + kkt['lastDocDate'] + '</td>')

                                #print ('<td>' + kkt['endPay'] + '</td>')
                                #print ('<td>' + delta_days(kkt['endPay']) + '</td>')
                                endPay = delta_days(kkt['endPay'])
                                if endPay != -1:
                                    if endPay < 30:
                                        print ('<td bgcolor="#FDDAC5"> Осталось ' + str(endPay) + ' дней </td>')
                                    else:
                                        print ('<td> Осталось ' + str(endPay) + ' дней </td>')
                                else:
                                    print ('<td>' + kkt['endPay'] + '</td>')

                                print ('<td>' + kkt['ofd'] + '</td>')
                                print ('<td>' + kkt['fnChangeDate'] + '</td>')
                                print ('<td>' + kkt['firmware'] + '</td>')
                                print ('<td>' + kkt['mac'] + '</td>')
                                print ('<td>' + kkt['memo'] + '</td>')
                                print ('<td>' + kkt['addDate'] + '</td>')
                                print ('</tr>')

                        print ('</table>')



print ('    </body>')
print ('</html>')

print (n)