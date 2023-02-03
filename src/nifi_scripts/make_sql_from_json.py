import json
import re
from org.apache.commons.io import IOUtils
from java.nio.charset import StandardCharsets
from org.apache.nifi.processor.io import StreamCallback

 # Define a subclass of StreamCallback for use in session.write()
class PyStreamCallback(StreamCallback):
  def __init__(self, table_name, schema_name):
        self.table_name=table_name
        self.schema_name=schema_name
  def convert_field(self,x):
        out = json.dumps(x,ensure_ascii=False)
        if isinstance(x,(dict)):
            out = out.replace("'","''").replace("[","{").replace("]","}")       
        elif isinstance(x,(list)):
            if not isinstance(x[0],(dict)):
                out = out.replace('"',"").replace('"',"").replace("[","{").replace("]","}")  
            else:
                out = out.replace("'","''")    
        else:
            out = re.sub(r"(\\r\\n)"," ", re.sub(r'^"|"$', '',out).replace("'","''").replace(r'\"','"')).strip() #\1+.replace('"',"")
        return "'"+out+"'" 

  def process(self, inputStream, outputStream):
    text = IOUtils.toString(inputStream,StandardCharsets.UTF_8) 
    obj = json.loads(text, encoding='utf-8')
    sql="INSERT INTO "+str(self.schema_name)+"."+str(self.table_name)+"("+", ".join(obj.keys())+") "+\
        "VALUES("+", ".join(map(lambda x: self.convert_field(x),obj.values()))+")"
           
    outputStream.write(sql.encode('utf-8'))
# end class
flowFile = session.get()
if(flowFile != None):
    table_name = flowFile.getAttribute('RouteText.Route')
    schema_name = flowFile.getAttribute('schema.name')
 #   try:   
    flowFile = session.write(flowFile, PyStreamCallback(table_name=table_name,schema_name=schema_name))
    session.transfer(flowFile, REL_SUCCESS)
 #   except Exception:
 #       session.transfer(flowFile, REL_FAILURE)    
    session.commit()