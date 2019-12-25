#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tapit

import json

tnkf = tapit.TTinkoffApiTrade('conf.txt')

print (tnkf.getData('/portfolio').content)
print (tnkf.getData('/portfolio/currencies').content)
print (tnkf.getData('/market/bonds').content)
print (tnkf.getData('/market/currencies').content)
print (tnkf.getData('/market/etfs').content)
print (tnkf.getData('/market/stocks').content)
print (tnkf.getData('/orders').content)