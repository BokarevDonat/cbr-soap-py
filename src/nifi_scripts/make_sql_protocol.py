import json
import re
from org.apache.commons.io import IOUtils
from java.nio.charset import StandardCharsets
from org.apache.nifi.processor.io import StreamCallback
from datetime import datetime

 # Define a subclass of StreamCallback for use in session.write()
class PyStreamCallback(StreamCallback):
  def __init__(self, table_name, schema_name, ts_ms):
        self.table_name=table_name
        self.schema_name=schema_name
        self.ts_ms=ts_ms

  def convert_field(self,x):
        out = json.dumps(x,ensure_ascii=False)
        out = re.sub(r"(\\r\\n)"," ", re.sub(r'^"|"$', '',out).replace("'","''")).strip()#.replace(r'\"','"')) #\1+.replace('"',"")
        return "'"+out+"'" 

  def process(self, inputStream, outputStream):
    text = IOUtils.toString(inputStream,StandardCharsets.UTF_8) 
    obj = json.loads(text, encoding='utf-8')
    obj['ts_ms']=datetime.fromtimestamp(long(self.ts_ms) / 1000).strftime('%Y-%m-%d %H:%M:%S.%f') 
    sql="INSERT INTO "+str(self.schema_name)+"."+str(self.table_name)+"("+", ".join('"'+str(item).lower()+'"' for item in obj.keys())+") "+\
        "VALUES("+", ".join(map(lambda x: self.convert_field(x),obj.values()))+")"
    outputStream.write(sql.encode('utf-8'))


flowFile = session.get()
if(flowFile != None):
    table_name = flowFile.getAttribute('RouteText.Route')
    schema_name = flowFile.getAttribute('schema.name')
    ts_ms = flowFile.getAttribute('kafka.timestamp')
   # try:
    flowFile = session.write(flowFile, PyStreamCallback(table_name=table_name,schema_name=schema_name, ts_ms=ts_ms))
    session.transfer(flowFile, REL_SUCCESS)
  #  except Exception:
  #    session.transfer(flowFile, REL_FAILURE) 
  #  finally: 
    session.commit()