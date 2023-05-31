import json
import re
from org.apache.commons.io import IOUtils
from java.nio.charset import StandardCharsets
from org.apache.nifi.processor.io import StreamCallback
from datetime import datetime

 # Define a subclass of StreamCallback for use in session.write()
class PyStreamCallback(StreamCallback):
  def __init__(self, attr):
        self.attr = attr
        self.schema_name = attr["schema_name"]
        self.table_name = attr["table_name"]
        attr.pop("schema_name")
        attr.pop("table_name")

  def convert_field(self,x):
        out = json.dumps(x,ensure_ascii=False)
        out = re.sub(r"(\\r\\n)"," ", re.sub(r'^"|"$', '',out).replace("'","''")).strip()#.replace(r'\"','"')) #\1+.replace('"',"")
        return "'"+out+"'" 

  def process(self, inputStream, outputStream):
    text = IOUtils.toString(inputStream,StandardCharsets.UTF_8) 
    obj = json.loads(text, encoding='utf-8')
    out=dict()
    for key, val in attr.items():
        out[key]=val
    out["rsbu-report-data"]=obj    
    sql="INSERT INTO "+str(self.schema_name)+"."+str(self.table_name)+"("+", ".join('"'+str(item).lower()+'"' for item in out.keys())+") "+\
        "VALUES("+", ".join(map(lambda x: self.convert_field(x),out.values()))+")"
    outputStream.write(sql.encode('utf-8'))


flowFileList = session.get(100)
if not flowFileList.isEmpty():
    for flowFile in flowFileList:
      attr = {'id': flowFile.getAttribute("id"),
              'counterparty': flowFile.getAttribute("counterparty"),
              'reportPeriod': flowFile.getAttribute("reportPeriod"),
              'reportType': flowFile.getAttribute("reportType"),
              'year': flowFile.getAttribute("year"),
              'schema_name': 'stg_rsbu',
              'table_name': 'rsbu'}
    # try:
      flowFile = session.write(flowFile, PyStreamCallback(attr))
      session.transfer(flowFile, REL_SUCCESS)
    # except Exception:
      #session.transfer(flowFile, REL_FAILURE) 
      #finally: 
session.commit()