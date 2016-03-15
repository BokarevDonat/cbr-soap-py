# SOAP interface to Bank of Russia (CBR) online data

- Text description of CBR backend <http://www.cbr.ru/scripts/root.asp>
- Some implementation in R <https://github.com/quantviews/CBR/>
- Related stackoverflow question <http://stackoverflow.com/questions/19708597/how-to-make-a-soap-request-by-using-soappy>

Implementation requirements:
- programming enviroment is python 3+, Anaconda build
- selected SOAP client is ```pysimplesoap```, ```SOAPpy``` and ```suds``` not installable
- ```Веб-сервис: www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx```

Tasks:

1. get ```Ruonia (FromDate, ToDate)``` rates for last month, described at <http://www.cbr.ru/scripts/Root.asp?PrtId=DWS> and 
  <http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx?op=Ruonia> (deliverable - sample code)
2. what is the difference between <http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx?op=Ruonia>(Dataset) and 
  <http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx?op=RuoniaXML>(XML)
3. explain what is service description - <http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx?WSDL>, how it can be accessed by 
  pysimplesoap.client (deliverable - sample code)?
4. how the data (responses) obtained from CBR website can be storred locally to minimise load on the CBR web site
5. what is MainInfoXML() - is this a duplicate of all other data, how it can be accessed (deliverable - sample code)


Work started at [cbr_soap.py](cbr_soap.py)
