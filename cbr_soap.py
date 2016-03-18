# -*- coding: utf-8 -*-
"""SOAP interface to Bank of Russia online data"""

# --- Comment --- 
# WSDL нужен чтобы обьявить приложению какая структура будет потребляться вэбсервисом
# вэбсервис - это обычный xml слушатель и отправитель также в формате XML
# следовательно результат можно распарсить и получить XML
# для понимания работы с вэбсервисом - приложение SoapUI

# --- Requirement ---
# pysimplesoap installed from git repo by:
# pip install -e git+git@github.com:pysimplesoap/pysimplesoap.git@07ab7217ccc2572d40ad36c73867fc9be8fe2794#egg=soap2py-master
# 
import pickle

from collections import OrderedDict
from datetime import datetime, timedelta
from os.path import exists

from bs4 import BeautifulSoup
from dateutil.parser import parse as parse_dt
from pysimplesoap.client import SoapClient

import requests


class SourceAddress():
    cbr_namespace = "http://web.cbr.ru/"
    url = "http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx"
    wsdl_url = "http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx?wsdl"


class DataSOAP(SourceAddress):
    cache_file_name = 'wsdl_cache.pickle'

    def update(self):
        client = SoapClient(wsdl=self.wsdl_url, namespace=self.cbr_namespace, trace=False)
        self.wsdl_info = client.wsdl_parse(self.wsdl_url)['DailyInfo']['ports']['DailyInfoSoap']['operations']

        for op in self.wsdl_info:
            # Convert unpicklable Struct to OrderedDict
            inputs = self.wsdl_info[op]['input']
            for x in inputs:
                inputs[x] = OrderedDict(inputs[x])

            # NOTE: outputs are unpicklable too. Delete them.
            del self.wsdl_info[op]['output']

        with open(self.cache_file_name, 'wb') as f:
            pickle.dump(self.wsdl_info, f)

    def load_local(self):
        with open(self.cache_file_name, 'rb') as f:
            self.wsdl_info = pickle.load(f)

    def __init__(self):
        if exists(self.cache_file_name):
            self.load_local()
        else:
            self.update()


class Parameters(DataSOAP):
    def __init__(self, operation):
        DataSOAP.__init__(self)
        op_info = self.wsdl_info[operation]
        self.dict = op_info['input'][operation]


class Response(SourceAddress):
    def __init__(self, body, headers):
        self.body = body
        self.headers = headers

    def get(self):
        response = requests.post(self.url, data=self.body, headers=self.headers)
        return BeautifulSoup(response.content, 'lxml')


def make_xml_parameter_string(operation, *args):
    """
    Make text string of parameters for POST XML based on *operation* name and *args
    """
    
    op_params = Parameters(operation).dict

    if len(args) != len(op_params):
        raise Exception('Operation %s requires args: %s' % (operation, op_params))

    param_string = ''
    for n, param in enumerate(op_params):
        value = args[n]
        if op_params[param] is datetime:
            value = value.strftime('%Y-%m-%d')
        if op_params[param] is bool:
            value = str(value).lower()
        param_string += '<web:%(param)s>%(val)s</web:%(param)s>' % {'param': param, 'val': value}
    
    return param_string


def make_body(operation, param_string):
    return """<?xml version="1.0" encoding="utf-8"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="%(ns)s">
    <soapenv:Header/>
    <soapenv:Body>
        <web:%(operation)s>
            %(params)s
        </web:%(operation)s>
    </soapenv:Body>
    </soapenv:Envelope>
    """ % {
        'ns': SourceAddress().cbr_namespace,
        'operation': operation,
        'params': param_string
    }


def make_headers(operation):
    return {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': 'http://web.cbr.ru/%s' % operation
    }


def call_cbr(operation, *args):
    """
    SOAP call to CBR backend
    """
    param_string = make_xml_parameter_string(operation, *args)    
    cbr_xml_body = make_body(operation, param_string)    
    headers      = make_headers(operation)
    return Response(cbr_xml_body, headers).get()

# not todo: CBR_Response(operation, *args) to include call_cbr() and make_*() functions


def as_dict(*t):
    return {'name': t[0], 'date': t[1], 'value': t[2]}


def yield_ruonia(start, end):
    # will change to CBR_Response('Ruonia', start, end).get()
    response = call_cbr('Ruonia', start, end)
    for x in response.find_all('ro'):
        dt = parse_dt(x.d0.text).strftime('%Y-%m-%d')
        ir = float(x.ruo.text)
        vol = float(x.vol.text)
        yield as_dict('ruonia_rate', dt, ir)
        yield as_dict('ruonia_vol', dt, vol)
        # intent: this flat data goes to sqlite later


def yield_valutes():
    response = call_cbr('EnumValutes', False)
    for x in response.find_all('enumvalutes'):
        result = {
            'code': x.vcode.text.strip(),
            'name': x.vname.text.strip(),
            'eng_name': x.vengname.text.strip(),
            'nominal': x.vnom.text.strip(),
            'char_code': x.vcharcode.text.strip() if x.vcharcode else None,
            'num_code': x.vnumcode.text.strip() if x.vnumcode else None,
            'common_code': x.vcommoncode.text.strip()}
        yield result


def yield_curs(start, end, code):
    response = call_cbr('GetCursDynamic', start, end, code)
    for x in response.find_all('valutecursdynamic'):
        yield {'date': parse_dt(x.cursdate.text), 'curs': float(x.vcurs.text)}


def yield_mkr(start, end):
    response = call_cbr('MKR', start, end)
    for x in response.find_all('mkr'):
        yield {
            'date': parse_dt(x.cdate.text),
            'p1': float(x.p1.text),
            'd1': float(x.d1.text) if x.d1 else None,
            'd7': float(x.d7.text) if x.d7 else None,
            'd30': float(x.d30.text) if x.d30 else None,
            'd90': float(x.d90.text) if x.d90 else None,
            'd180': float(x.d180.text) if x.d180 else None,
            'd360': float(x.d360.text) if x.d360 else None,
        }



# todo: try write one or several other yield functions 
# - MKR (FromDate, ToDate) Ставки межбанковского кредитного рынка XSD 
# - EnumValutes(Seld) Справочник по кодам валют, содержит полный перечень валют котируемых Банком России - чтобы узнать когды валют
# - GetCursDynamic(FromDate, ToDate, ValutaCode) Получение динамики ежедневных курсов валюты
#      доллар - R01235
#      евро - R01239
        

if __name__ == "__main__":

    # todo: make proper assert to check get_operation_parameters output, maybe several asserts 
    # assert DataSOAP().get_operation_parameters('Ruonia') == {'fromDate': <class 'datetime.datetime'>, 'ToDate': <class 'datetime.datetime'>}
 
    #start = datetime.now() - timedelta(days=30)
    #end = datetime.now()
    start = datetime(2016, 3, 13)
    end = datetime(2016, 3, 15)
    assert make_xml_parameter_string('Ruonia', start, end) == '<web:fromDate>2016-03-13</web:fromDate><web:ToDate>2016-03-15</web:ToDate>'

    response = call_cbr('Ruonia', start, end)
    print(type(response))

    #todo:
    # check in assert this *response* is instance of class <class 'bs4.BeautifulSoup'>
    # check *response* content as decoded string equals *reference_response_string* with whitespace removed
            
    assert list(yield_ruonia(start, end)) == [as_dict('ruonia_rate', '2016-03-14',  11.07), 
                                              as_dict('ruonia_vol',  '2016-03-14', 150.46), 
                                              as_dict('ruonia_rate', '2016-03-15',  11.1 ), 
                                              as_dict('ruonia_vol',  '2016-03-15', 185.87)]
                                              
    # todo: correct if something fails below
    import pandas as pd

    valutes = pd.DataFrame(yield_valutes())
    valutes.index = valutes.name
    valutes.to_csv('valutes.csv')

    usd_rate = pd.DataFrame(yield_curs(start, end, 'R01235'))
    usd_rate.index = usd_rate.date
    usd_rate.to_csv('usd_rate.csv')

    mkr = pd.DataFrame(yield_mkr(start, end))
    mkr.index = mkr.date
    mkr.to_csv('mkr.csv')

    def make_df(gen):
        df = pd.DataFrame(gen)
        df = df.pivot(columns='name', values='value', index='date')
        df.index = pd.to_datetime(df.index)
        return df      
   
    ruonia_df = make_df(yield_ruonia(start, end))
    ruonia_df.to_csv('ruonia.txt')
    print(ruonia_df.to_csv())
        
    # df = pd.DataFrame(yield_ruonia(start, end))
    ## reshape/pivot using date/value
    # df = df.pivot(columns='name', values='value', index='date')
    # df.index = pd.to_datetime(df.index)

            
# SOAP UI response to *cbr_body*
reference_response_string = """<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
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
