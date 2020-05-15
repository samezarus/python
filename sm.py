#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import json

from datetime import datetime
import cx_Oracle # https://zen.yandex.ru/media/internet_lab/ustanovka-oracle-instant-client-na-ubuntu-5d10c998f56fb600afe2762d
import os
import smtplib
from email.mime.text import MIMEText
from email.header    import Header

os.environ["NLS_LANG"] = "Russian.AL32UTF8" # Для кириллицы в Оракле

host = 'xxx'
port = '1521'
uName = 'xxx'
passwrd = 'xxx'
dbName = 'xxxx'

conn = cx_Oracle.connect(uName+'/'+passwrd+'@'+host+':'+port+'/'+dbName)
#print (conn.version)

cur = conn.cursor()

#cur.execute("SELECT * FROM SUPERMAG.SMActs WHERE EXECDATE = TO_DATE ('12.05.2020', 'dd.mm.yyyy')")
cur.execute("SELECT SUPERMAG.smdocuments.ID, SUPERMAG.SMActs.EXECDATE FROM SUPERMAG.smdocuments, SUPERMAG.SMActs WHERE SUPERMAG.smdocuments.LOCATION = 206 AND SUPERMAG.smdocuments.DOCTYPE = 'AC' AND  SUPERMAG.smdocuments.DOCSTATE > 0 AND SUPERMAG.smdocuments.ID = SUPERMAG.SMActs.ID AND SUPERMAG.SMActs.EXECDATE BETWEEN TO_DATE ('18.05.2020', 'dd.mm.yyyy') AND TO_DATE ('22.05.2020', 'dd.mm.yyyy')")

result = cur.fetchall()

text = ''

for item in result:
    #print (item)
    text = text + '\n' + str(item[0]) + ' - ' + str(item[1])
#print (str(result))
print (text)

conn.close


m_HOST = 'smtp.xxx.ru'
m_PORT = 25
m_FROM  = 'xxx@xxx.ru'
m_LOGIN = 'xxx@xxx.ru'
m_PASS  = 'xxxxxx'
m_TO = 'xyxyxy@xxx.ru'
m_TEXT    = str(text)

m_BODY = MIMEText(m_TEXT, 'plain', 'utf-8')
m_BODY['Subject'] = Header('Важное сообщение', 'utf-8')
m_BODY['From'] = m_FROM
m_BODY['To'] = m_TO

m_server = smtplib.SMTP(m_HOST, m_PORT)
m_server.login(m_LOGIN, m_PASS)
m_server.sendmail(m_FROM, [m_TO], m_BODY.as_string())
m_server.quit()
