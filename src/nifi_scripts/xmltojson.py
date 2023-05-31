#!/usr/bin/python3
import sys
import xmltodict, json
import os 
file_name =sys.stdin.readline().rstrip()
with open(file_name, mode='r', encoding='utf-8') as data:
    o = xmltodict.parse(data.read(), encoding='utf-8', attr_prefix='', cdata_key='text', process_namespaces=True, namespace_separator=',', namespaces={
    "http://localhost/ExchangeDMZ": None, 
    "http://www.w3.org/2003/05/soap-envelope": None, 
    "http://www.w3.org/2003/05/soap-envelope/": None, 
    "http://www.w3.org/2001/XMLSchema-instance": None, 
    "http://schemas.xmlsoap.org/wsdl/": None, 
    "http://schemas.xmlsoap.org/wsdl/soap12/": None,
    "http://schemas.xmlsoap.org/wsdl/soap/": None,
    "http://schemas.xmlsoap.org/soap/envelope/": None,
    "http://schemas.xmlsoap.org/ws/2004/09/policy": None,
    "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd": None,
    "http://www.w3.org/2001/XMLSchema": None,
    "ExchangeDMZ": None
    })
    with open(file_name+'.json', 'w', encoding='utf-8') as f:
        json.dump(o, f, ensure_ascii=False, indent=4)
os.remove(file_name)