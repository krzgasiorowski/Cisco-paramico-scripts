import sys
import json
import os
import datetime
import pandas as pd
import openpyxl
from mac_vendor_lookup import MacLookup

print("*"*9 + " Enter the excel file name with cmds results (with sheets:sh_mac, sh_arp, sh_int, sh_cdp)" + "*" *9)
DATA_FILE=str(input("File name, or press ENTER for default[./output/Output_summary-last.xlsx]:").strip() or "./output/Output_summary-last.xlsx")
if os.path.isfile(DATA_FILE):
    pass
else:  
    print(f"No such file: {DATA_FILE}")
    sys.exit()

#print("update MAC vendor list...")
#MacLookup().update_vendors()

dfmac=pd.read_excel(DATA_FILE, sheet_name="sh_mac")
dfmac.rename(columns={'destination_address':'mac_address'},inplace=True)
dfmac.rename(columns={'destination_port':'port'},inplace=True)
dfmac.drop ('type', axis=1, inplace=True)
dfmac['port'] = dfmac['port'].apply(lambda x: (((x.strip("[")).strip("]")).strip("'")))

dfarp=pd.read_excel(DATA_FILE, sheet_name="sh_arp")
dfarp.rename(columns={'device':'device_arp'},inplace=True)
dfarp.drop (['type','protocol',"interface","location",'age'], axis=1, inplace=True)

dfint=pd.read_excel(DATA_FILE, sheet_name="sh_int")
dfint.rename(columns={'name':'description'},inplace=True)
dfint.drop (['fc_mode','status','location','type'], axis=1, inplace=True)

dfcdp=pd.read_excel(DATA_FILE, sheet_name="sh_cdp")
dfcdp.rename(columns={'local_interface':'port'},inplace=True)
dfcdp['port'] = dfcdp['port'].apply(lambda x: (((((x.replace(" ","")).replace("Gig","Gi")).replace("Ten","Te")).replace("Two","Tw")).replace("Fas","Fa")))
dfcdp.drop (['neighbor_interface',"location","capability"], axis=1, inplace=True)
#print(dfcdp)
print ("merging MAC and ARP tables...")
df = pd.merge(dfmac, dfarp, left_on=['mac_address'], right_on = ['mac_address'], how='left')

print ("merging INTERFACES table...")
df = pd.merge(df, dfint, left_on=['port','device'], right_on = ['port','device'], how='left')

print ("removing trunks...")
df = df[df['vlan_id_y'].str.contains('trunk') == False]
dfarp.drop (['device_arp'], axis=1, inplace=True)

print ("merging CDP table...")
df = pd.merge(df, dfcdp, left_on=['port','device'], right_on = ['port','device'], how='left')

print ("updating MAC vendor...")
vendorcolumne = []

for m in df['mac_address']:
       try:
          vendorcolumne.append(MacLookup().lookup(m))
       except:
          vendorcolumne.append("Unknown")
df['vendor'] =vendorcolumne

writer = pd.ExcelWriter(DATA_FILE, engine = 'openpyxl', mode='a')
df.to_excel(writer, index=False, sheet_name="endpoints")               
writer.close()
print ("*"*25 + " End " + "*" *25)