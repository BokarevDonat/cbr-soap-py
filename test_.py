from datetime import datetime
from bs4 import BeautifulSoup
import cbr_soap

SAMPLE_DATE_START = datetime(2016, 3, 13)
SAMPLE_DATE_END = datetime(2016, 3, 15)

def test_param_string():
    WEB_1 = '<web:fromDate>2016-03-13</web:fromDate><web:ToDate>2016-03-15</web:ToDate>'
    assert WEB_1 == cbr_soap.Response('Ruonia', SAMPLE_DATE_START, SAMPLE_DATE_END).make_xml_parameter_string()

def test_cbr_call(): 
    response = cbr_soap.Response('Ruonia', SAMPLE_DATE_START, SAMPLE_DATE_END).get()
    assert(isinstance(response, BeautifulSoup))

    reference = BeautifulSoup(reference_ruonia_xml_string().strip(), 'lxml')
    assert(reference.prettify() == response.prettify())

def test_yield_ruonia():
    RUONIA_VALUES = [('ruonia_rate', '2016-03-14',  11.07), 
                     ('ruonia_vol',  '2016-03-14', 150.46), 
                     ('ruonia_rate', '2016-03-15',  11.10), 
                     ('ruonia_vol',  '2016-03-15', 185.87)]
                     
    RUONIA_SAMPLE = list(cbr_soap.as_dict(*x) for x in RUONIA_VALUES)
    ruonia_response = list(cbr_soap.yield_ruonia(start = SAMPLE_DATE_START, end = SAMPLE_DATE_END))    

    assert RUONIA_SAMPLE == ruonia_response 

def test_ruonia_df():
    ruonia_df = cbr_soap.Stream("ruonia", SAMPLE_DATE_START, SAMPLE_DATE_END).df # make_df(yield_ruonia(start, end))
    SAMPLE_CSV_REPR = "'date,ruonia_rate,ruonia_vol\\n2016-03-14,11.07,150.46\\n2016-03-15,11.1,185.87\\n'"
    #import pdb; pdb.set_trace()
    assert SAMPLE_CSV_REPR == ruonia_df.to_csv().__repr__()     

#test_ruonia_df()
    

def test_Parameters():
    # todo: make proper assert to check get_operation_parameters output, maybe several asserts 
    # assert cbr_soap.Parameters('Ruonia') == {'fromDate': <class 'datetime.datetime'>, 'ToDate': <class 'datetime.datetime'>}
    pass
    
def reference_ruonia_xml_string():
    return """<?xml version="1.0" encoding="utf-8"?>
<html>
<body>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
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
</body>
</html>
"""
