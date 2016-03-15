# Example for SOAP interface to Bank of Russia online data 

# 1. Code below is from stack overflow - cannot run it because pip fails on SOAPpy dependencies

# from SOAPpy import SOAPProxy
# from SOAPpy import Types

cbr_namespace = "http://web.cbr.ru/"
cbr_url = "http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx"
cbr_soapaction = "http://web.cbr.ru/GetCursOnDate"
# input = Types.dateType(name = (namespace, "On_date"))

# proxy = SOAPProxy(url, namespace = namespace, soapaction = soapaction)
# proxy.config.debug = 1
# proxy.GetCursOnDate(input)


# 2. code below does not work, lots of errors

# from suds.client import Client
# url = "http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx"
# client = Client(url)
# print(client)


# 3. pysimplesoap client

from pysimplesoap.client import SoapClient, SimpleXMLElement

# create the webservice client
client = SoapClient(
        location = cbr_url,
        #cache = cache,
        #proxy = parse_proxy(proxy),
        #cacert = cacert,
        #timeout = TIMEOUT,
        #ns = "ejb", 
        soap_server = cbr_soapaction,  
        namespace = cbr_namespace,
        #soap_ns = "soapenv",
        #trace = trace
        )
print(client)