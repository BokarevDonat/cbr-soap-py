# Example for SOAP interface to Bank of Russia online data 

# -*- coding: utf-8 -*-
 
# WSDL нужен чтобы обьявить приложению какая структура будет потребляться вэбсервисом
# вэбсервис - это обычный xml слушатель и отправитель также в формате XML
# следовательно результат можно распарсить и получить XML
# вот пример кода для работы с вэбсервисом без всяких мудрых библиотек:
# вам для понимания работы с вэбсервисом не хватило просто приложения SoapUI. 
# посмотрите как в нем все работает и все поймете

from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from dateutil.parser import parse as parse_dt
from pysimplesoap.client import SoapClient

import requests


cbr_namespace = "http://web.cbr.ru/"
url = "http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx"
wsdl_url = "http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx?wsdl"

client = SoapClient(wsdl=wsdl_url, namespace=cbr_namespace, trace=False)
wsdl_info = client.wsdl_parse(wsdl_url)['DailyInfo']['ports']['DailyInfoSoap']['operations']


def call_cbr(operation, *args):
    """
    Make SOAP call to cbr.
    """
    op_info = wsdl_info[operation]
    op_params = op_info['input'][operation]

    if len(args) != len(op_params):
        raise Exception('Operation %s requires args: %s' % (operation, op_params))

    params = ''
    for n, param in enumerate(op_params):
        value = args[n]
        if op_params[param] is datetime:
            value = value.strftime('%Y-%m-%d')
        if op_params[param] is bool:
            value = str(value).lower()
        params += '<web:%(param)s>%(val)s</web:%(param)s>' % {'param': param, 'val': value}

    cbr_body = """<?xml version="1.0" encoding="utf-8"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="%(ns)s">
    <soapenv:Header/>
    <soapenv:Body>
        <web:%(operation)s>
            %(params)s
        </web:%(operation)s>
    </soapenv:Body>
    </soapenv:Envelope>
    """ % {
        'ns': cbr_namespace,
        'operation': operation,
        'params': params
    }

    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': 'http://web.cbr.ru/%s' % operation
    }

    response = requests.post(url, data=cbr_body, headers=headers)
    return BeautifulSoup(response.content, 'lxml')


#start = datetime.now() - timedelta(days=30)
#end = datetime.now()


start = datetime(2016, 3, 13)
end = datetime(2016, 3, 15)

response = call_cbr('Ruonia', start, end)

results = []
for x in response.find_all('ro'):
    results.append((parse_dt(x.d0.text).strftime('%Y-%m-%d'), float(x.ruo.text), float(x.vol.text)))


target_result = [
    ('2016-03-14', 11.0700, 150.4600), ('2016-03-15', 11.1000, 185.8700)]


assert results == target_result


# SOAP UI response to *cbr_body*
reference_response = """<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
   <soap:Body>
      <RuoniaResponse xmlns="http://web.cbr.ru/">
         <RuoniaResult>
            <xs:schema id="Ruonia" xmlns="" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:msdata="urn:schemas-microsoft-com:xml-msdata">
               <xs:element name="Ruonia" msdata:IsDataSet="true" msdata:UseCurrentLocale="true">
                  <xs:complexType>
                     <xs:choice minOccurs="0" maxOccurs="unbounded">
                        <xs:element name="ro">
                           <xs:complexType>
                              <xs:sequence>
                                 <xs:element name="D0" msdata:Caption="Дата" type="xs:dateTime" minOccurs="0"/>
                                 <xs:element name="ruo" msdata:Caption="Ставка, %" type="xs:decimal" minOccurs="0"/>
                                 <xs:element name="vol" msdata:Caption="Объем сделок,по которым произведен расчет ставки RUONIA, млрд. руб." type="xs:decimal" minOccurs="0"/>
                              </xs:sequence>
                           </xs:complexType>
                        </xs:element>
                     </xs:choice>
                  </xs:complexType>
               </xs:element>
            </xs:schema>
            <diffgr:diffgram xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">
               <Ruonia xmlns="">
                  <ro diffgr:id="ro1" msdata:rowOrder="0">
                     <D0>2016-03-14T00:00:00+03:00</D0>
                     <ruo>11.0700</ruo>
                     <vol>150.4600</vol>
                  </ro>
                  <ro diffgr:id="ro2" msdata:rowOrder="1">
                     <D0>2016-03-15T00:00:00+03:00</D0>
                     <ruo>11.1000</ruo>
                     <vol>185.8700</vol>
                  </ro>
               </Ruonia>
            </diffgr:diffgram>
         </RuoniaResult>
      </RuoniaResponse>
   </soap:Body>
</soap:Envelope>
"""
