import requests
from requests.auth import HTTPBasicAuth
from lxml import etree
from lxml import html
from xml.etree import ElementTree
import urllib3
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import sys
import os
import pandas as pd
import openpyxl
import json
import nmap
nm = nmap.PortScanner()

print("Enter the excel file name with endpoints's IP (sheets:endpoints, column:ip_address),")
DATA_FILE=str(input("eg. name.: ./output/Scan_summary-last.xlsx : ").strip() or "./output/Scan_summary-last.xlsx")
if os.path.isfile(DATA_FILE):
    pass
else:  
    print(f"No such file: {DATA_FILE}")
    sys.exit()



#Preparing collumnes as emty tables
columneSystem = []

#load Excel as data frame
dfENDPOINTS=pd.read_excel(DATA_FILE, sheet_name="endpoints")
for IP in dfENDPOINTS['ip_address']:
       #try:
            if IP == IP : # trick for ignore nan objects
                print (f"collecting info for IP: {IP}")
                nm.scan(hosts=IP, arguments='-sn --unprivileged')  
                print(nm.scaninfo())
                #RESPJSON = json.loads(RESP)
                #print(json.dumps(RESPJSON, indent=4))             
                #print( RESPJSON[0]['names'], sep=",")
                #columneSystem.append(RESPJSON[0]['names'])

            else: 
                columneSystem.append("")
                continue
       #except:
            #print ("Excel format incorrect")
        #    continue
#dfENDPOINTS['System'] = columneSystem

#writer = pd.ExcelWriter(DATA_FILE, engine = 'openpyxl', mode='a')
#dfENDPOINTS.to_excel(writer, index=False, sheet_name="nmap")               
#writer.close()
print ("*"*24 + " End " + "*" *24)