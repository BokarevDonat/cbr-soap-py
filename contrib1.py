# https://gist.github.com/Fak3/4ec8fabab0f97fe2bfd8

# EP:
#
# Used following to install suds:
#     conda install --channel https://conda.anaconda.org/IOOS suds-jurko
#
# Traceback (most recent call last):
#  File "contrib1.py", line 9, in <module>
#    from suds.client import Client
#  File "C:\Users\Евгений\Anaconda3\lib\site-packages\suds\__init__.py", line 28, in <module>
#    from version import __build__, __version__
# ImportError: No module named 'version'
# 



# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from datetime import datetime, timedelta
from dateutil.parser import parse as parse_dt
from suds.client import Client
from suds.xsd.doctor import Import, ImportDoctor

cbr_namespace = "http://web.cbr.ru/"

url = "http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx?wsdl"
imp = Import('http://www.w3.org/2001/XMLSchema', location='http://www.w3.org/2001/XMLSchema.xsd')
imp.filter.add(cbr_namespace)
client = Client(url, doctor=ImportDoctor(imp))

start = datetime.now() - timedelta(days=30)
end = datetime.now()
result = client.service.Ruonia(start, end)

for x in result.diffgram.Ruonia.ro:
    print("Дата %s" % parse_dt(x.D0).strftime('%Y.%m.%d'))
    print("Ставка, %s %%" % x.ruo)
    print("Объем сделок %s млрд. руб\n" % x.vol)