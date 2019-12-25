#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import httplib2
import json
#
class httpResult():
    resp    = ''
    content = ''
#
class TTinkoffApiTrade():
    confFiliPath = ''
    apiURL       = 'https://api-invest.tinkoff.ru/openapi'
    token        = ''
    #
    def __init__(self, _confFilePath):
        self.confFiliPath = _confFilePath
        self.getConf()
    #
    def getConf(self):
        confFile   = open(self.confFiliPath, 'r')
        confParams = json.load(confFile)
        self.token = confParams['token']
    #
    def getData(self, qString):
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