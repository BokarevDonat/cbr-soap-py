import json
import re
from datetime import datetime
from org.apache.commons.io import IOUtils
from java.nio.charset import StandardCharsets
from org.apache.nifi.processor.io import StreamCallback

 # Define a subclass of StreamCallback for use in session.write()
class PyStreamCallback(StreamCallback):
  def __init__(self,request, schema_name, table_name):
        self.request=request
        self.schema_name= schema_name
        self.table_name=table_name

  def convert_field(self,x):
    out = json.dumps(x,ensure_ascii=False)
    if isinstance(x,(basestring)):
        out = re.sub(r"(\\r\\n)"," ", re.sub(r'^"|"$', '',out).replace("'","''").replace(r'\"','"')).strip().replace('"',"")
    elif isinstance(x,(dict)):
            out = out.replace("'","''")    
    return "'"+out+"'" 

  def process(self, inputStream, outputStream):
    text = IOUtils.toString(inputStream,StandardCharsets.UTF_8) 
    obj = json.loads(text, encoding='utf-8')[0]
    out = dict()
    out['request']=self.request
    out['response'] = obj['Body']
    sql="INSERT INTO "+str(self.schema_name)+"."+str(self.table_name)+"("+", ".join(map(lambda x: '"'+str(x).lower()+'"',out.keys()))+") "+\
        "VALUES("+", ".join(map(lambda x: self.convert_field(x),out.values()))+")"
    outputStream.write(sql.encode('utf-8'))

    

# end class                                                                       
flowFile = session.get()
if(flowFile != None):
    request = flowFile.getAttribute('request')
    schema_name = flowFile.getAttribute('schema.name')
    table_name = flowFile.getAttribute('table.name')
    flowFile = session.write(flowFile, PyStreamCallback(request=request, 
                                                        schema_name=schema_name, 
                                                        table_name=table_name))
    session.transfer(flowFile, REL_SUCCESS)

    session.commit()