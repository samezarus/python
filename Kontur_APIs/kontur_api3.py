#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pip3 install httplib2
# pip3 install openpyxl
# pip3 install pymongo
# pip3 install pymysql
# pip3 install psutil

import httplib2, urllib
import json
import openpyxl
import pymongo
import pymysql
from datetime import datetime
import psutil


def runScriptQuery(killQuery):
    count = 0
    for p in psutil.pids():
        if psutil.Process(p).name().find('python') != -1:
            for item in psutil.Process(p).cmdline():
                if item == __file__:
                    count +=1
                    if killQuery == True:
                        parent = psutil.Process(psutil.Process(p).pid)
                        for child in parent.children(recursive=True):
                            child.kill()
                        parent.kill()
    return count

class TResponse():
    #
    def __init__(self, urlStr, method, cookies):
        self.status = '0'
        self.jsonDoc  = json.loads('{}')
        #
        self.url     = urlStr
        self.method  = method
        self.cookies = cookies
        #
        self.get()
    #
    def get(self):
        h = httplib2.Http('.cache')
        (resp, content) = h.request(uri=self.url, method=self.method, headers=self.cookies)
        #
        self.status = str(resp.status)
        if self.status == '200':
            self.jsonDoc = json.loads(content.decode("utf-8"))
        del h

class TKontur():
    ofd_api_key  = '' # ключ интегратора
    SID          = '' #
    cookies      = {}
    cookieDomain = '' #
    endPoint     = '' # площадка
    mail         = '' # емаил авторизации
    passwd       = '' # пароль авторизации

    authStatusCode = '' # код статуса авторизации

    sgoServer   = ''
    sgoUser     = ''
    sgoPassword = ''
    sgoDb       = ''

    lastError = ''

    addonXlsxFile = '' # экселька Райгородского

    logFileName = 'log.txt'
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self):
        self.logFile = open(self.logFileName, "a+")

        conn = pymongo.MongoClient('localhost', 27017)
        db   = conn['TKontur2']

        self.dbOrgs   = db['orgs']
        self.dbSpsKks = db['spskkts']
        self.dbSps    = db['sps']
        self.dbKks    = db['kkts']
        self.tickets  = db['tickets']

        #self.dbOrgs.drop()
        self.dbSpsKks.drop()
        #self.tickets.drop()
    # ------------------------------------------------------------------------------------------------------------------
    def to_log (self, logStr):
        if len(logStr) > 0:
            self.logFile.write(str(datetime.now()) + ' - ' + logStr+ '\n')

    # ------------------------------------------------------------------------------------------------------------------
    def end_pay_format(self, s):
        # "28.07.2019 - 28.08.2020" to "28.08.2020"
        result = s
        if len(s) == 23:
            if s[2] == '.' and s[5] == '.' and s[11] == '-' and s[15] == '.' and s[18] == '.':
                result = s[13:23]

        return result
    # ------------------------------------------------------------------------------------------------------------------
    def nowRuDate(self):
        s = str(datetime.now())
        s = s[8:10] + '.' + s[5:7] + '.' + s[0:4]
        return s
    # ------------------------------------------------------------------------------------------------------------------
    def newCookie(self):
        self.cookies = {'Cookie': 'ofd_api_key=' + self.ofd_api_key + ';auth.sid=' + self.SID}
    # ------------------------------------------------------------------------------------------------------------------
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
    # ------------------------------------------------------------------------------------------------------------------
    def save_or_update(self, collection, field, jsonDoc):
        # save or update document in mongo db
        if collection.find({field: str(jsonDoc[field])}).count() == 0:
            collection.save(jsonDoc)
        else:
            collection.update({field: str(jsonDoc[field])}, jsonDoc)
    # ------------------------------------------------------------------------------------------------------------------
    def get_ticket(self, orgId, kktRegNumber, fnId, docNumb, strForLog):
        urlStr = self.endPoint + '/v1/lk/organizations/' + orgId + '/cashboxes/' + kktRegNumber + '/fns/' + fnId + '/documents/' + str(docNumb)
        self.newCookie()
        ticketResp = TResponse(urlStr, 'GET', self.cookies)
        #
        if ticketResp.status == '200':
            self.to_log(strForLog)
            self.tickets.save(ticketResp.jsonDoc)
        #
        del ticketResp
    # ------------------------------------------------------------------------------------------------------------------
    def get_inf(self, getTickets):
        if self.authStatusCode == '200':
            urlStr  = self.endPoint + 'v1/organizations' # Запрос на получение списка "Организаций" доступных пользователю
            self.newCookie()
            orgsResp = TResponse(urlStr, 'GET', self.cookies)

            if orgsResp.status == '200':
                for org in orgsResp.jsonDoc:
                    orgId   = org['id']        # id "Организации"
                    orgName = org['shortName'] # Короткое назване "Организации"
                    #
                    self.save_or_update(self.dbOrgs, 'id', org)
                    #
                    urlStr = self.endPoint + 'v1/lk/organizations/' + orgId + '/cashboxes' # Запрос на получение "Точек продаж" и их "ККТ"
                    self.newCookie()
                    spsKktsResp = TResponse(urlStr, 'GET', self.cookies)

                    if spsKktsResp.status == '200':
                        self.dbSpsKks.save(spsKktsResp.jsonDoc)
                        spsCount = len(spsKktsResp.jsonDoc['items']) # Количество "Точек продаж" у "Организации"

                        for i in range(spsCount):
                            spId = spsKktsResp.jsonDoc['items'][i]['salesPointId']     # ID "Точки продаж"
                            spName = spsKktsResp.jsonDoc['items'][i]['salesPointName'] # Имя "Точки продаж"
                            #
                            jsonDoc = {'salesPointId':spId, 'salesPointName':spName, 'organizationId':orgId} # Вспомогательная коллекция, что бы не грузить выборкой из инфы о ККТ
                            self.save_or_update(self.dbSps, 'salesPointId', jsonDoc)                         # Добавляем/Обновляем инф. о "Точке продаж"
                            #
                            kktsCount = len(spsKktsResp.jsonDoc['items'][i]['cashboxStates']) # Количество "ККТ" у "Точки продаж" у "Организации"
                            #
                            for j in range(kktsCount):
                                kktName = spsKktsResp.jsonDoc['items'][i]['cashboxStates'][j]['cashboxName'] #
                                #
                                jsonDoc = spsKktsResp.jsonDoc['items'][i]['cashboxStates'][j] #
                                self.save_or_update(self.dbKks, 'cashboxRegNumber', jsonDoc)  # Добавляем/Обновляем инф. о "ККТ"
                                #
                                if getTickets == True:
                                    allDocCount  = spsKktsResp.jsonDoc['items'][i]['cashboxStates'][j]['lastDocumentsByType']['cashReceipt']['cashboxDocumentId']['fiscalDocumentNumber']
                                    kktRegNumber = spsKktsResp.jsonDoc['items'][i]['cashboxStates'][j]['cashboxRegNumber']
                                    fnId         = spsKktsResp.jsonDoc['items'][i]['cashboxStates'][j]['fnSerialNumber']

                                    findTicket = self.tickets.find({'cashbox.regNumber.value': kktRegNumber, 'documentInfo.fnSerialNumber.value': fnId})
                                    docNumb = findTicket.count()

                                    for k in range(docNumb, allDocCount):
                                        strForLog = 'get doc | ' + orgName + ' | ' + spName + ' | ' + kktName + ' | ' + str(k +1)
                                        self.get_ticket(orgId, kktRegNumber, fnId, k +1, strForLog)
# ----------------------------------------------------------------------------------------------------------------------

Kontur = TKontur()
#
Kontur.ofd_api_key   = '' # ключ для доступа личного кабинета через браузер
Kontur.SID           = ''
Kontur.cookieDomain  = '.kontur.ru'
Kontur.endPoint      = 'https://ofd-api.kontur.ru/'
Kontur.mail          = '
Kontur.passwd        = ''
Kontur.sgoUser       = ''
Kontur.sgoPassword   = ''
Kontur.sgoDb         = ''
Kontur.addonXlsxFile = 'addon.xlsx'
#
Kontur.authenticate_by_pass()
#
Kontur.get_inf(False)
#
# Получение чеков для задания в Cron (cron -e)
#if runScriptQuery(True) == 1:
#    Kontur.get_inf(True)
#    Kontur.logFile.close()

