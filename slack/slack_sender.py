#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import sys
from datetime import datetime

#hook    = 'https://hooks.slack.com/services/<hook>' # https://sameza.slack.com/apps/manage/custom-integrations
#channel = '#py_test'

#to = 'https://hooks.slack.com/services/<hook>=#py_test'

# ----------------------------------------------------------------------

to      = sys.argv[1]
subject = sys.argv[2]
text    = sys.argv[3]

#text = subject + '\n' + text

def get_hook (s):
    result = ''
    i = s.find('=')
    if i > -1:
        result = s[0:i]
    return result

def get_channel (s):
    result = ''
    i = s.find('=')
    if i > -1:
        result = s[i+1:len(s)]
    return result

# ------------------------------------------------------------------------

hook    = get_hook(to)
channel = get_channel(to)
username = 'webhookbot'

s = 'payload={"channel":"'+channel+'", "username": "'+username+'", "attachments":[{"color": "#C0392B", "title":"'+subject+'", "text": "'+text+'"}]}'
mess = bytes(s, 'utf-8')
req = urllib.request.Request(hook, data=mess)

response = urllib.request.urlopen(req)
