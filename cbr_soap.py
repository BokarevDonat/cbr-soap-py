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

CBR_NAMESPACE = "http://web.cbr.ru/"
SOAP_URL = "http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx"
WSDL_URL = "http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx?wsdl"


class WSDL(object):
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
        """ Convert unpicklable Struct to OrderedDict """
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
        client = SoapClient(wsdl=WSDL_URL, namespace=self.cbr_namespace, trace=False)
        self.wsdl_info = client.wsdl_parse(WSDL_URL)['DailyInfo']['ports']['DailyInfoSoap']['operations']
        self.convert_wsdl_info_to_pickable()
        self.save_local_copy()

    def get_input_params(self, operation):
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
        if operation not in self.wsdl_info.keys():
            raise KeyError("Operation not recognised:" + operation)
        op_info = self.wsdl_info[operation]
        return op_info['input'][operation]


class SoapRequest(object):
    def __init__(self, operation, *args):
        self.operation = operation
        self.args = args
        self.wsdl_info = WSDL()
        self.body = self.make_body()
        self.headers = self.make_headers()

    def send(self):
        """ Send POST request. Return xml tree of response. """
        response = requests.post(SOAP_URL, data=self.body, headers=self.headers)
        return BeautifulSoup(response.content, 'lxml')

    def make_xml_parameter_string(self):
        """ Make string of parameters for POST XML based on *operation* name and *args"""

        op_params = self.wsdl_info.get_input_params(self.operation)

        if len(self.args) != len(op_params):
            raise Exception('Operation %s requires following arguements: %s' % (self.operation, op_params))

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
            'ns': CBR_NAMESPACE,
            'operation': self.operation,
            'params': self.param_string
        }

    def make_headers(self):
        return {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'http://web.cbr.ru/%s' % self.operation
        }


def call_cbr(operation, *args):
    request = SoapRequest(operation, *args)
    response = request.send()
    return response


def as_dict(*t):   
    return {'name': t[0], 'date': t[1], 'value': t[2]}

def get_date(txt):
    return parse_dt(txt).strftime('%Y-%m-%d')

def yield_ruonia(start, end):
    response = call_cbr('Ruonia', start, end)
    for x in response.find_all('ro'):
        dt = get_date(x.d0.text)
        ir = float(x.ruo.text)
        vol = float(x.vol.text)
        yield as_dict('ruonia_rate', dt, ir)
        yield as_dict('ruonia_vol', dt, vol)

        
def yield_currencies():
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
        yield get_date(x.cursdate.text), float(x.vcurs.text)

        
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
    for date, val in yield_curs(start, end, currency_code):
        yield as_dict('USDRUR_CBR', date, val)


def yield_eur(start, end):
    currency_code = 'R01239'
    for date, val in yield_curs(start, end, currency_code):
        yield as_dict('EURRUR_CBR', date, val)

    
class Frame():

    def __init__(self, gen):
        self.make_dataframe(gen)
    
    def make_dataframe(self, gen):
        self.raw_df = pd.DataFrame(gen)
        df = self.raw_df.pivot(columns='name', values='value', index='date')
        df.index = pd.to_datetime(df.index)
        self.df = df
    
    def to_csv(self, path):
        self.df.to_csv(path)
        
    def to_excel(self, path):
        self.df.to_excel(path)
        
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
                self.start = datetime.now() - timedelta(days=30)

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
        # note: better insert_many(gen) with chucks and update - very slow if many datapoints
        for d in gen:
            self.data_table.upsert(d, keys = ['date','name','value'])
    

class Database(Stream):
    
    def __init__(self):
        pass
    
    def update_all(self):
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
    import ipdb; ipdb.set_trace()
    
    # 'currencies.csv' has useful currency codes like EUR, USD may use for column names in dataframe
    #save_currencies()
    
    # usd/rur exhange rate
    usd_rate = Frame("usdrur", start, end).to_csv()
    
    # eur/rur exhange rate
    eur_rate = Frame("eurrur", start, end).to_csv()
    
    # mkr, cтавки и объемы межбанковского кредитного рынка
    mkr = Frame("mkr", start, end).to_csv()    
   
    # ставка ruonia
    ruonia_df = Stream("ruonia", start, end).to_csv()
    #Frame("ruonia", start, end).to_sql()
    
    d = Database()
    d.update_all()
    # d.freeze()
    
    out = Outputs()
    print(out.df)
    out.write()

    
    
# -------------------------------------------------------------------------------------------------------------------------------

# Mostly done / для комментариев
# - [ ] немного на свой вкус переструктурировать классы - от вас нужен будет комментарий по результатам что у меня получилось 
# *** нужен комментарий по качеству реализации классов. мне не особо нравится что yield* функции где-то висят, но убирать их в какой-то класс тоже не хочется

# response = Response('MKR', start, end).get()
# Более понятна была бы прямая логика: делаем soap-request, получаем response. Примерно вот так:
# response = cbr_call('MKR', start, end)
#
# Методы построения запроса make_xml_parameter_string() и пр. сейчас находятся в классе Response,
# хотя по идее им место в request
#
# Класс SourceAddress можно вообще расформировать и убрать из иерархии. Он определяет некие константы,
# которые используются в нескольких местах (WSDL\Request). Такие константы принято именовать uppercase'ом,
# и можно поместить прямо в модуле:
# CBR_NAMESPACE = "http://web.cbr.ru/"
#
# class Parameters(WDSL)
# параметры по идее являются частью WSDL-информации, а не подклассом. Лучше добавить в класс WSDL метод, получающий
# dict параметров, а класс Parameters расформировать.
#
#


# - [ ] assert из main переписываю в тесты py.test дальше добавляем тесты по мере добавления нового кода 
# *** нужны предложения по расширению tests coverage в критических местах + 1 todo в test_.py
#
# Пока классы, функции и схема данных модуля не стабилизируется - переписывание тестов будет отнимать время
# Лучше пока отложить


# - [ ] несколько рядов данных упаковываю в датафрейм, его пишу в новый файл xls 
# *** вроде все работает 

# - [ ] через dataset https://dataset.readthedocs.org/en/latest/ приделаю базу данных SQLite для кеширования данных


# todo:
# - [ ] как необходмио знать на стадии заполнения какие имена переменных у нас в базе данных, причем в разбивке по тематикам (источникам)
#       + этот список переменных испоьзвать для сортировки колонок в датафрейме Outputs().df
#       видимо где-то нужен список переменных завести для этого
#       вопрос не в том чтобы из базы посмотреть список уникальных переменных, а иметь свой список переменных в виед константы для 
#       управления колонками + что измениться если писать cbr.xls на несколько шитов по тематикам
#
#  Нужно уточнить как именно хочется управлять колонками. Как использовать список имен переменных для сортировки - тоже непонятно.
#
#  xls на несколько шитов по тематикам - хочется понять какие данные относятся к каким тематикам (шитам).
#  Точно также как в DSAR_Currency.xls? Или не совсем?
#
#
# - [ ] смотрим механизм как определять последнюю дату загруженных данных и обновлять их начиная с этой даты будет ли эта дата одна для всех серий и где хранится
#
# Тут нужно определить что для нас является целостностью. Какие данные мы ожидаем видеть в какие дни.
# После этого можно будет реализовать проверку перед записью в БД. Также определиться что делать если
# получили от ЦБ неполные данные?
#
#
# - [ ] аналогично нужно как-то знать исходныю дату заполнения каждйо operations
#
# Что имеется ввиду? Дату когда был закеширован wsdl-info?
#
#
# - [ ] requirements.txt?
#
# git+git@github.com:pysimplesoap/pysimplesoap.git@07ab7217ccc2572d40ad36c73867fc9be8fe2794#egg=pysimplesoap
# lxml==3.5.0
# beautifulsoup4==4.4.1
# pandas==0.18.0
# python-dateutil==2.5.0
# requests==2.9.1


# not todo / later, но можно комментирвоать 
# - [ ] переместить часть закомментированного кода в скриптовой части в тесты - по аналогии с ruonia
# - [ ] try check why usd and eur exchange rates are only one data point, should be two for these start and end dates (two working days)
# - [ ] дописываем импорт других данных из doc/roots.md 
# - [ ] возможно делаем код пакетом, чтобы убрать в отдельную папку, а итоговые файлы и методы высокого уровня (типа UpdateDataset - обновить все данные), тоже в корневую папку. 9. подумать как можно автоматически запускать такой updatedataset на удаленной машине (у меня была попытка, но не очень получилось)
# - [ ] save_currencies() может быть отдельным шитом в cbr.xls или отдельным файлом
# - [ ] оформеление xls файла - https://github.com/epogrebnyak/rosstat-806-regional/blob/master/xls_write.py

# very much later / не комментируем
# - [ ] смотрю как можно писать данные в существующий файл через xlwings 

# -------------------------------------------------------------------------------------------------------------------------------

# коментарий - конечное использование 
# 1) пользователь  должен иметь доступ к файлy cbr.xls и cbr.txt (cbr.csv), просто скачивать его и линковать свои файлы к нему 
# 2) (под вопросом) программа должна с помощью xlwings вписать данные в файл пользователя, например, такой как https://github.com/epogrebnyak/cbr-soap-py/blob/master/doc/DSAR_Currency.xls 
# 3) администратор должен иметь возможность запустить исходное наполнение пустой базы данных или обновление по текущую дату заполненной ранее базы данных 
# 4) пользователь должен иметь возможность извлечь один или несколько рядов данных из базы данных с помощью функции входа, аргументы - название показателя, дата начала, дата окончания. 
