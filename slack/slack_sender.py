#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
from datetime import datetime

hook     = 'https://hooks.slack.com/services/<hook>' # https://sameza.slack.com/apps/manage/custom-integrations
channel  = '#py_test'
username = 'webhookbot'
text     = 'This is test in '+str(datetime.now())

#mess = b'payload={"channel":"#py_test", "username": "webhookbot", "text": "This is test from python"}'
#s = 'payload={"channel":"#py_test", "username": "webhookbot", "text": "This is test in '+str(datetime.now())+'"}'

s = 'payload={"channel":"'+channel+'", "username": "'+username+'", "text": "'+text+'"}'
mess = bytes(s, 'utf-8')
req = urllib.request.Request(hook, data=mess)

response = urllib.request.urlopen(req)
print (response)
