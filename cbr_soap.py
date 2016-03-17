# Example for SOAP interface to Bank of Russia online data 

# -*- coding: utf-8 -*-
 
# WSDL нужен чтобы обьявить приложению какая структура будет потребляться вэбсервисом
# вэбсервис - это обычный xml слушатель и отправитель также в формате XML
# следовательно результат можно распарсить и получить XML
# вот пример кода для работы с вэбсервисом без всяких мудрых библиотек:
# вам для понимания работы с вэбсервисом не хватило просто приложения SoapUI. 
# посмотрите как в нем все работает и все поймете
 
from bs4 import BeautifulSoup
from dateutil.parser import parse as parse_dt

import requests


url = "http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx"
headers = {'content-type': 'text/xml'} 
cbr_body = """<?xml version="1.0" encoding="utf-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="http://web.cbr.ru/">
   <soapenv:Header/>
   <soapenv:Body>
      <web:Ruonia>
         <web:fromDate>2016-03-13</web:fromDate>
         <web:ToDate>2016-03-15</web:ToDate>
      </web:Ruonia>
   </soapenv:Body>
</soapenv:Envelope>
"""

headers = {
    'Content-Type': 'text/xml; charset=utf-8',

    #
    # note: seems to work without length parameter
    # , 'Content-Length': len(cbr_body)
    #

    'SOAPAction': 'http://web.cbr.ru/Ruonia'
}

r = requests.get(url, headers=headers)
resp = requests.post(url, data=cbr_body, headers=headers)
print (resp.content.decode('utf-8'))


# todo (not critical):
# fix encoding: in resp.content cyrillic letters are shown as \xd0\xbf\xd0\xbe \xd0\xba\xd0\xbe\xd1\x82\xd0\xbe
#               need to show them as in *reference_response*.
#               better if obtained in proper encoding, rather than decoded as string locally

# todo (critical):
#               write parse_xml() to contained get data
#               must pass assert below

target_result = [
    ('2016-03-14', 11.0700, 150.4600), ('2016-03-15', 11.1000, 185.8700)]


def parse_xml(response_content):
    soup = BeautifulSoup(response_content, 'lxml')
    results = []
    for x in soup.find_all('ro'):
        results.append((parse_dt(x.d0.text).strftime('%Y-%m-%d'), float(x.ruo.text), float(x.vol.text)))
    return results


assert parse_xml(resp.content) == target_result


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
