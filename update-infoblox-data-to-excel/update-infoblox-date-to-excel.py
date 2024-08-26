import requests
from requests.auth import HTTPBasicAuth
from lxml import etree
from lxml import html
from xml.etree import ElementTree
import urllib3
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import sys
import pwinput
import os
import pandas as pd
import openpyxl
import json


INFOBLOX_IP=str(input("Server Infoblox IP or FQDN:").strip())
if not INFOBLOX_IP : print("Warning: server IP not entered")
USERNAME=str(input("Server Infoblox Username:").strip())
if not USERNAME : print("Warning: not username entered")
PASSWORD = pwinput.pwinput("Password:")
if not PASSWORD : print("Warning: Empty password entered")

DATA_FILE=str(input("Enter the excel file name with endpoints's IP (sheets:endpoints, column:ip_address), eg name.: ./output/Scan_summary-last.xlsx").strip() or "./output/Scan_summary-last.xlsx")
if os.path.isfile(DATA_FILE):
    pass
else:  
    print(f"No such file: {DATA_FILE}")
    sys.exit()

session = requests.Session()
session.headers.update({'Accepts': 'application/json'})

#Preparing collumnes as emty tables
columneNames = []
columneTypes =[]
columneUsages =[]
columneIs_conflict=[]
columneInfobloxMAC=[]

#load Excel as data frame
dfENDPOINTS=pd.read_excel(DATA_FILE, sheet_name="endpoints")
for IP in dfENDPOINTS['ip_address']:
       try:
            if IP == IP : # trick for ignore nan objects
                print (f"collecting info for IP: {IP}")
                URL1 = "https://"+INFOBLOX_IP+"/wapi/v2.11/ipv4address?ip_address="+IP

                REQ = session.get(url=URL1, auth=HTTPBasicAuth(USERNAME, PASSWORD),verify=False)
                RESP = (REQ.content)
                RESPJSON = json.loads(RESP)
                #print(json.dumps(RESPJSON, indent=4))             
                print( RESPJSON[0]['names'], RESPJSON[0]['types'],RESPJSON[0]['usage'],RESPJSON[0]['is_conflict'],RESPJSON[0]['mac_address'], sep=",")
                columneNames.append(RESPJSON[0]['names'])
                columneTypes.append(RESPJSON[0]['types'])
                columneUsages.append(RESPJSON[0]['usage'])
                columneIs_conflict.append(RESPJSON[0]['is_conflict'])
                columneInfobloxMAC.append(RESPJSON[0]['mac_address'])
            else: 
                columneNames.append("")
                columneTypes.append("")
                columneUsages.append("")
                columneIs_conflict.append("")
                columneInfobloxMAC.append("")
                continue
       except:
            print ("Excel format incorrect")
            continue
dfENDPOINTS['Infoblox names'] = columneNames
dfENDPOINTS['Infoblox types'] = columneTypes
dfENDPOINTS['Infoblox usages'] = columneUsages
dfENDPOINTS['DHCP is conflict'] = columneIs_conflict
dfENDPOINTS['Infoblox MAC'] = columneInfobloxMAC
writer = pd.ExcelWriter(DATA_FILE, engine = 'openpyxl', mode='a')
dfENDPOINTS.to_excel(writer, index=False, sheet_name="infoblox")               
writer.close()
print ("*"*24 + " End " + "*" *24)