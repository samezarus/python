# -*- coding: utf-8 -*-

# Главная страница API - http://help.vetrf.ru/wiki/%D0%92%D0%B5%D1%82%D0%B8%D1%81.API
# http://help.vetrf.ru/wiki/Подсистема_обработки_заявок_в_Ветис.API#.D0.9C.D0.B5.D1.80.D0.BA.D1.83.D1.80.D0.B8.D0.B9

import zeep
from requests import Session
from requests.auth import HTTPBasicAuth
import pymongo

class TVetis():
    uName = ''
    uPass = ''
    apiKey = ''
    issuerId = ''
    serviceId = ''
    #
    def __init__(self, uName, uPass):
        self.session = Session()
        self.session.auth = HTTPBasicAuth(uName, uPass)

    def GetRussianEnterpriseList(self, listOptionsDic, enterpriseDic):
        """
        Операция GetRussianEnterpriseList предназначена для получения списка предприятий, зарегистрированных на территории Российской Федерации
        http://help.vetrf.ru/wiki/GetRussianEnterpriseList
        """
        wsdl = 'http://api.vetrf.ru/schema/platform/services/2.0-last/EnterpriseService_v2.0_production.wsdl'
        client = zeep.Client(wsdl, transport=zeep.Transport(session=self.session))

        listOptions = client.get_type('ns1:ListOptions')()
        listOptions['count'] = listOptionsDic['count']
        listOptions['offset'] = listOptionsDic['offset']

        enterprise = client.get_type('ns3:Enterprise')()

        result = client.service.GetRussianEnterpriseList(listOptions, enterprise)
        return result

    def GetBusinessEntityUser(self):
        # НЕ РАБОТАЕТ
        wsdl = 'http://api.vetrf.ru/schema/platform/services/2.0-last/ams-mercury-g2b.service_v2.0_production.wsdl'
        client = zeep.Client(wsdl, transport=zeep.Transport(session=self.session))

        application = client.get_type('ns2:Application')()
        # app.applicationId = 'a1b2c3d4e5' # ns1:UUID
        # app.status = '' # ns2:ApplicationStatus
        application['serviceId'] = self.serviceId  # xsd:Name # Код запрашиваемого сервиса (системы, к которой обращается пользователь).
        application['issuerId'] = self.issuerId  # ns1:UUID # Идентификатор хозяйствующего субъекта от имени которого происходит обращение к Ветис.API
        application['issueDate'] = '2020-06-23T14:40:00'  # xsd:dateTime # Дата и время обращения пользователя к заявочной системе. Устанавливается разработчиком клиентской системы.
        # app.rcvDate = '' # xsd:dateTime
        # app.prdcRsltDate = '' # xsd:dateTime
        application['data'] = client.get_type('ns2:ApplicationDataWrapper')()  # ns2:ApplicationDataWrapper # Сведения о заявке
        application['data']['applicationData'] = client.get_type('ns2:ApplicationData')()  # ns2:ApplicationData
        # app.result = '' # ns2:ApplicationResultWrapper
        # app.errors = '' # ns2:BusinessErrorList

        appData = client.get_type('ns4:GetBusinessEntityUserRequest')()
        appData['localTransactionId'] = 'a10003'
        appData.initiator = client.get_type('ns6:User')()
        appData['initiator']['login'] = self.uName
        appData['user'] = client.get_type('ns6:User')()
        appData['user']['login'] = self.uName

        application['data'].getBusinessEntityUserRequest = client.get_element('ns4:getBusinessEntityUserRequest')()
        application['data'].getBusinessEntityUserRequest = appData

        result = client.service.submitApplicationRequest(self.apiKey, application)
        return result

########################################################################################################################
uName = '...'
uPass = '...'
vetis = TVetis(uName, uPass)
vetis.apiKey = '...'
vetis.issuerId = '...'
vetis.serviceId = 'mercury-g2b.service:2.0'

###
listOptionsDic = {'count': 2, 'offset': 0}
enterpriseDic = {}
print(vetis.GetRussianEnterpriseList(listOptionsDic, enterpriseDic))
###
#print(vetis.GetBusinessEntityUser())
