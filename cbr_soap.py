# -*- coding: utf-8 -*-
"""SOAP interface to Bank of Russia online data"""

# --- Comment --- 
# WSDL нужен чтобы обьявить приложению какая структура будет потребляться вэбсервисом
# вэбсервис - это обычный xml слушатель и отправитель также в формате XML
# следовательно результат можно распарсить и получить XML
# для понимания работы с вэбсервисом - приложение SoapUI - <https://www.soapui.org/>

# --- Requirement ---
# pysimplesoap installed from git repo by:
# pip install -e git+git@github.com:pysimplesoap/pysimplesoap.git@07ab7217ccc2572d40ad36c73867fc9be8fe2794#egg=soap2py-master
# warning: installs to repo 

import pickle
import requests
import dataset
import os

from collections import OrderedDict
from datetime import datetime, timedelta
import pandas as pd
    
from bs4 import BeautifulSoup
from dateutil.parser import parse as parse_dt
from pysimplesoap.client import SoapClient

CSV_FOLDER = 'csv'


class SourceAddress():
    cbr_namespace = "http://web.cbr.ru/"
    url = "http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx"
    wsdl_url = "http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx?wsdl"


class WDSL(SourceAddress):
    
    cache_file_name = 'wsdl_cache.pickle'
    
    def __init__(self):
        if os.path.exists(self.cache_file_name):
            self.load_local_copy()
        else:
            self.load_from_cbr()

    def load_local_copy(self):
        with open(self.cache_file_name, 'rb') as f:
            self.wsdl_info = pickle.load(f)
    
    def convert_wsdl_info_to_pickable(self):    
        """Convert unpicklable Struct to OrderedDict"""
        for op in self.wsdl_info:
        
            # pointer links to 'self.wsdl_info', all changes in pointer are recorded in 'self.wsdl_info'
            pointer = self.wsdl_info[op]['input']
            for x in pointer:
                pointer[x] = OrderedDict(pointer[x])

            # 'outputs' are unpicklable and not used here, delete them from 
            del self.wsdl_info[op]['output']
    
    def save_local_copy(self):        
        with open(self.cache_file_name, 'wb') as f:
            pickle.dump(self.wsdl_info, f) 

    def load_from_cbr(self):
        client = SoapClient(wsdl=self.wsdl_url, namespace=self.cbr_namespace, trace=False)
        self.wsdl_info = client.wsdl_parse(self.wsdl_url)['DailyInfo']['ports']['DailyInfoSoap']['operations']
        self.convert_wsdl_info_to_pickable() 
        self.save_local_copy()

        
class Parameters(WDSL):
    """ Get WSDL parameters based on *operation* name
     
        Accepts as *operation*:
        
        'GetReutersCursOnDate', 'Repo_debt', 'SwapDynamic', 'mrrf', 'ROISfix', 'MKRXML', 'SwapDayTotalXML', 
        'Overnight', 'BiCurBacketXML', 'XVolXML', 'SwapInfoSellUSDVolXML', 'GetReutersCursDynamic', 'GetCursOnDate', 
        'BiCurBaseXML', 'EnumValutesXML', 'GetCursOnDateXML', 'DV', 'RuoniaXML', 'Repo_debtXML', 'GetSeldCursOnDateXML', 
        'RepoDebtUSD', 'NewsInfo', 'GetLatestReutersDateTime', 'DragMetDynamic', 'EnumReutersValutesXML', 'SwapInfoSellUSDVol', 
        'GetLatestDate', 'EnumValutes', 'OstatDynamicXML', 'SwapDayTotal', 'DVXML', 'OstatDepo', 'MKR', 'Bauction', 
        'SwapDynamicXML', 'SwapMonthTotalXML', 'BiCurBacket', 'SaldoXML', 'DepoDynamic', 'NewsInfoXML', 'GetCursDynamic', 
        'Coins_baseXML', 'BiCurBase', 'DragMetDynamicXML', 'ROISfixXML', 'Coins_base', 'BauctionXML', 'MainInfoXML', 'Saldo', 
        'Ruonia', 'AllDataInfoXML', 'GetLatestDateTime', 'mrrf7D', 'SwapInfoSellUSD', 'mrrfXML', 'SwapMonthTotal', 'DepoDynamicXML', 
        'GetLatestDateSeld', 'GetLatestDateTimeSeld', 'OmodInfoXML', 'GetReutersCursDynamicXML', 'mrrf7DXML', 'EnumReutersValutes', 
        'FixingBaseXML', 'RepoDebtUSDXML', 'SwapInfoSellUSDXML', 'GetCursDynamicXML', 'GetReutersCursOnDateXML', 'OvernightXML', 
        'OstatDynamic', 'OstatDepoXML', 'GetSeldCursOnDate', 'XVol', 'FixingBase'
    """
    
    def __init__(self, operation):
        WDSL.__init__(self)
        if operation not in self.wsdl_info.keys():
            raise KeyError ("Operation not recognised:" + operation)
        op_info = self.wsdl_info[operation]
        self.dict = op_info['input'][operation]

        
class POST_Request(SourceAddress):
    def __init__(self, body, headers):
        self.body = body
        self.headers = headers

    def get(self):
        response = requests.post(self.url, data=self.body, headers=self.headers)
        return BeautifulSoup(response.content, 'lxml')

class Response():

    def make_xml_parameter_string(self):
        """ Make string of parameters for POST XML based on *operation* name and *args"""
        
        op_params = Parameters(self.operation).dict

        if len(self.args) != len(op_params):
            raise Exception('Operation %s requires following arguements: %s' % (operation, op_params))

        self.param_string = ''
        for i, param in enumerate(op_params):
            value = self.args[i]
            if op_params[param] is datetime:
                value = value.strftime('%Y-%m-%d')
            if op_params[param] is bool:
                value = str(value).lower()
            self.param_string += '<web:%(param)s>%(val)s</web:%(param)s>' % {'param': param, 'val': value}
        
        return self.param_string


    def make_body(self):
    
        self.make_xml_parameter_string()        
    
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
            'operation': self.operation,
            'params': self.param_string
        }

    def make_headers(self):
        return {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'http://web.cbr.ru/%s' % self.operation
        }


    def __init__(self, operation, *args):
        """SOAP call to CBR backend"""
        
        self.operation = operation
        self.args = args
        xml_body = self.make_body()    
        headers = self.make_headers()
        self.response = POST_Request(xml_body, headers).get()
    
    def get(self):
        return self.response
        
def as_dict(*t):
    # todo: must check t[0] is datetime, t[1] is date, t[2] is float or None
    return {'name': t[0], 'date': t[1], 'value': t[2]}

def get_date(txt):
    return parse_dt(txt).strftime('%Y-%m-%d')

def yield_ruonia(start, end):
    response = Response('Ruonia', start, end).get()
    for x in response.find_all('ro'):
        dt = get_date(x.d0.text)
        ir = float(x.ruo.text)
        vol = float(x.vol.text)
        yield as_dict('ruonia_rate', dt, ir)
        yield as_dict('ruonia_vol', dt, vol)

        
def yield_currencies():
    response = Response('EnumValutes', False).get()
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
    response = Response('GetCursDynamic', start, end, code).get()
    for x in response.find_all('valutecursdynamic'):
        yield as_dict('USDRUR_CBR', get_date(x.cursdate.text), float(x.vcurs.text))

        
def yield_mkr(start, end):

    """Generator for Cтавки и объемы межбанковского кредитного рынка."""

    names = { 1:'MIBID_RUB_IR', 2:'MIBOR_RUB_IR' 
    , 3:'MIACR_RUB_IR',    4:'MIACR_IG_RUB_IR'
    , 5:'MIACR_RUB_VOL',   6:'MIACR_IG_RUB_VOL'
    , 7:'MIACR_B_RUB',     8:'MIACR_B_RUB_VOL'
    , 9:'MIBID_USD_IR',   10:'MIBOR_USD_IR'
    , 11:'MIACR_USD_IR',  12:'MIACR_IG_USВ'
    , 13:'MIACR_USD_VOL', 14:'MIACR_IG_USD_VOL'
    , 15:'MIACR_B_USD_IR',16:'MIACR_B_USD_VOL'}
        
    """тип 1-MIBID(RUB), 2-MIBOR(RUB), 
    3-MIACR(RUB), 4-MIACR-IG(RUB), 
    5-MIACR(RUB, оборот), 6-MIACR-IG(RUB, оборот), 
    7-MIACR-B(RUB), 8-MIACR-B(RUB, оборот), 
    9-MIBID(USD), 10-MIBOR(USD), 
    11-MIACR(USD), 12- MIACR-IG(USВ), 
    13-MIACR(USD, обороты), 14-MIACR-IG(USD, обороты), 
    15-MIACR-B(USD), 16 MIACR-B(USD, обороты)"""
    
    def _filter(z):   
            return float (z.text) if z else None

    response = Response('MKR', start, end).get()
    
    for x in response.find_all('mkr'):
        #todo: pd.to_datetime
        dt = get_date(x.cdate.text)
        var_code = int(x.p1.text)
        prefix = 'MBK_' + names[var_code] + "_"        
    
        # IMPORTANT: yield_* functions must return values by data point, using as_dict()
        yield as_dict(prefix + 'd1',   dt, _filter(x.d1)  )
        yield as_dict(prefix + 'd7',   dt, _filter(x.d7)  )
        yield as_dict(prefix + 'd30',  dt, _filter(x.d30) )
        yield as_dict(prefix + 'd90',  dt, _filter(x.d90) )
        yield as_dict(prefix + 'd180', dt, _filter(x.d180))
        yield as_dict(prefix + 'd360', dt, _filter(x.d360))


    

def yield_usd(start, end):
    currency_code = 'R01235'
    return yield_curs(start, end, currency_code)
    
def yield_eur(start, end):
    currency_code = 'R01239'
    return yield_curs(start, end, currency_code)    

    
class Frame():

    def __init__(self, gen):
        self.make_dataframe(gen)
    
    def make_dataframe(self, gen):
        df = pd.DataFrame(gen)
        #dix = df.duplicated
        #df = df.pivot(columns='name', values='value', index='date')
        #df.index = pd.to_datetime(df.index)
        self.df = df
    
    def to_csv(self, path):
        self.df.to_csv(path)
        
    @property
    def dataframe():
        return self.df 

    
class Stream(Frame):

    db = dataset.connect('sqlite:///cbr.db')
    data_table = db['datapoints']

    functions = {'ruonia':yield_ruonia, 'usdrur': yield_usd, 'eurrur':yield_eur, 'mkr':yield_mkr}

    def __init__(self, operation, start=None, end=None):
        self.operation = operation  
        self.clean_interval(start, end)
        Frame.__init__(self, self.get_stream())
    
    def clean_interval(self, start, end):
        """Start, end dates based on incomplete inputs""" 
        self.start, self.end = None, None 
        if start is not None and end is not None:  
            self.start, self.end = start, end       
        elif end is None:
            self.end = datetime.now()
            if start is None:
                self.start = datetime.now() - timedelta(days=7)

        # not todo: check start, end type 
        #           check start > end
        #           ambigious behaviour on one input 
        
    def get_stream(self):
        #warning: unstable order of id,value,name,date -> later affects Database.freeze() output 
        return self.functions[self.operation](self.start, self.end)  
    
    def to_csv(self):
        filename = os.path.join(CSV_FOLDER, self.operation +  ".csv")
        self.df.to_csv(filename)
        return self.df
    
    def to_sql(self):
        gen = self.get_stream()
        # note: better insert_many(gen) with chucks and update
        for d in gen:
            self.data_table.upsert(d, keys = ['date','name','value'])
    

class Database(Stream):
    
    def __init__(self):
        pass
    
    def insert_all(self):
        for ticker in self.functions.keys():
            print("Updating: " + ticker)
            Stream(ticker).to_sql()  
    
    def freeze(self):
        dataset.freeze(self.data_table.all(), format='csv', filename='db.txt')   
    
    #def get_latest_date(self):
    #    # not todo: return latest (common) date in for all time series 
    #    pass
    
    def dicts(self):  
        return [dict(od) for od in self.data_table.all()]    

class Outputs(Frame):
    def __init__(self):        
        Frame.__init__(self, gen = Database().dicts())
        
    def write(self):    
        self.to_csv("cbr.txt")
        self.to_excel("cbr.xls")
        
def save_currencies():
    currencies = pd.DataFrame(yield_currencies())
    currencies.index = currencies.name
    currencies.to_csv(os.path.join(CSV_FOLDER,'currencies_info.csv'))

    
if __name__ == "__main__":
        
    start = datetime(2016, 3, 13)
    end = datetime(2016, 3, 15)
    
    # 'currencies.csv' has useful currency codes like EUR, USD may use for column names in dataframe
    #save_currencies()
    
    # todo: try check why usd and eur exchange rates are only one data point, should be two for these start and end dates (two woring days)
    # usd/rur exhange rate
    #usd_rate = Frame("usdrur", start, end).to_csv()
    
    # eur/rur exhange rate
    #eur_rate = Frame("eurrur", start, end).to_csv()
    
    # mkr, cтавки и объемы межбанковского кредитного рынка
    #mkr = Frame("mkr", start, end).to_csv()    
   
    # ставка ruonia
    #ruonia_df = Stream("ruonia", start, end).to_csv()
    #Frame("ruonia", start, end).to_sql()
    
    d = Database()
    # d.insert_all()
    # d.freeze()
    # print(d.dicts())
    
    df = Outputs().df[['name', 'value', 'date']]
    df.index = df.date
    dix = df.duplicated(keep = False)
    assert len(df[dix]) == 0
    #problem: I do not understand where there is duplication in my data
    #         but this duplication causes pivot method to fail below
    df.pivot(columns='name', values='value', index='date')
    
    
# -------------------------------------------------------------------------------------------------------------------------------
#Tenatative list: 

# подготовительное
# done 1. немного на свой вкус переструктурировать классы - от вас нужен будет комментарий по результатам что у меня получилось 
# done 2. assert из main переписываю в тесты py.test дальше добавляем тесты по мере добавления нового кода 

# итоговая выгрузка
# todo 3. несколько рядов данных упаковываю в датафрейм, его пишу в новый файл xls 
# todo 4. смотрю как можно писать данные в существующий файл через xlwings 

# кеширование
# todo 5. вместе смотрим механизм как определять последнюю дату загруженных данных и обновлять их начиная с этой даты 
#         см. get_latest_date() method in DatabaseManager

# done 6. через dataset https://dataset.readthedocs.org/en/latest/ приделаю базу данных SQLite для кеширования данных
# todo 6+1. как добывать данные из базы данных для фрейма? где-то нужен список всех переменных, причем в разбивке по фреймам

# расширение
# not todo 7. дописываем импорт других данных из doc/roots.md 
# not todo 8. возможно делаем код пакетом, чтобы убрать в отдельную папку, а итоговые файлы и методы высокого уровня (типа UpdateDataset - обновить все данные), тоже в корневую папку. 9. подумать как можно автоматически запускать такой updatedataset на удаленной машине (у меня была попытка, но не очень получилось)

# todo 9. небольшие todo в тексте cbr_soap.py и test_.py 