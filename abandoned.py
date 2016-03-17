# 1. Code below is from stack overflow - cannot run it because pip fails on SOAPpy dependencies

# from SOAPpy import SOAPProxy
# from SOAPpy import Types

namespace = "http://web.cbr.ru/"
url = "http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx"
soapaction = "http://web.cbr.ru/GetCursOnDate"
# input = Types.dateType(name = (namespace, "On_date"))
# proxy = SOAPProxy(url, namespace = namespace, soapaction = soapaction)
# proxy.config.debug = 1
# proxy.GetCursOnDate(input)

# 2. pysimplesoap client

from pysimplesoap.client import SoapClient, SimpleXMLElement

# create the webservice client
client = SoapClient(wsdl = "http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx?wsdl")
        
print(client)