import sys
import json
import os
import datetime
import pandas as pd
import xlsxwriter
import openpyxl
from mac_vendor_lookup import MacLookup

print("*"*16 + "Enter the excel file name with MACs(sheet name 'mac, columne name 'mac_address')"  + "*" *16)
DATA_FILE=str(input("File name:").strip() )
if os.path.isfile(DATA_FILE):
    pass
else:  
    print(f"No such file: {DATA_FILE} in current directory")
    sys.exit()

#writer = pd.ExcelWriter("Output_summary-"+time1+".xlsx", engine = 'openpyxl')
#print("update MAC vendor list...")
#MacLookup().update_vendors()

df=pd.read_excel(DATA_FILE, sheet_name="mac")

print ("updating MAC vendor")
vendorcolumne = []

for m in df['mac_address']:
       try:
          vendorcolumne.append(MacLookup().lookup(m.strip( )))
          print ((MacLookup().lookup(m)))
       except:
          vendorcolumne.append("Unknown")
df['vendor'] =vendorcolumne

writer = pd.ExcelWriter(DATA_FILE, engine = 'openpyxl', mode='a')
df.to_excel(writer, index=False, sheet_name="mac_vendor")               
writer.close()
print ("*"*20 + " End " + "*" *20)