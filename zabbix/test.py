#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import httplib2
import urllib

########################################################################################################################
def url_get(url, token):
    url = url + '/zabbix/api_jsonrpc.php'

    header = {'Authorization': 'Bearer ' + token}
    h      = httplib2.Http('.cache')
    (resp, content) = h.request(uri=url, method='GET', headers=header)

    urlResult = {
        'resp'   : resp,
        'content': json.loads(content.decode("utf-8")),
    }

    return urlResult
########################################################################################################################
def url_post(url, headers, params):
    # Универсальная функция

    h               = httplib2.Http('.cache')
    (resp, content) = h.request(uri=url, method='POST', headers=headers, body=params)

    result = {}
    result.update({'resp': resp})
    result.update({'status': resp['status']})
    if resp['content-length'] != '0':
        result.update({'content': json.loads(content.decode("utf-8"))})
    else:
        result.update({'content': {}})

    return result
########################################################################################################################
def get_inf (params):
    #
    url       = 'http://192.168.1.69' + '/zabbix/api_jsonrpc.php'
    headers   = {'Content-Type': 'application/json-rpc'}
    urlResult = url_post(url, headers, params)

    result = {}

    if len(urlResult['content']) > 0:
        urlResult = urlResult['content']

        if urlResult.get('error') != None:
            result.update({'error': urlResult['error']['message']+' '+urlResult['error']['data']})
            print(result['error'])
        else:
            result.update({'error': ''})

        if urlResult.get('result') != None:
            result.update({'result': urlResult['result']})
        else:
            result.update({'result': {}})

    return result
########################################################################################################################
def get_auth_id (user, password):
    # Аутентификация

    result = ''

    params    = '{"jsonrpc": "2.0","method": "user.login","params": {"user": "' + user + '","password": "' + password + '"},"id": 1,"auth": null}'
    urlResult = get_inf(params)
    if urlResult['error'] == '':
        result = urlResult['result']

    return result
########################################################################################################################
def get_groups(authID):
    # Получение списка групп узлов сети
    # item: {'groupid': '5', 'name': 'Discovered hosts', 'internal': '1', 'flags': '0'}

    result = []

    if authID != '':
        params    = '{"jsonrpc": "2.0","method": "hostgroup.get","params": {"output": "extend","sortfield": "name"},"id": 1,"auth": "' + authID + '"}'
        urlResult = get_inf(params)
        if urlResult['error'] == '':
            result = urlResult['result']

    return result
########################################################################################################################
########################################################################################################################
########################################################################################################################
user     = 'Admin'
password = 'zabbix'

authID = get_auth_id(user, password)

groups = get_groups(authID)

for item in groups:
    print(item)