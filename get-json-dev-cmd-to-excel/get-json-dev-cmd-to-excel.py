import sys
import pwinput
from netmiko import ConnectHandler
from netmiko import NetmikoAuthenticationException
from netmiko import NetmikoTimeoutException
import json
import os
import datetime
import logging
import pandas as pd
import openpyxl
import pprint
time1 = (datetime.datetime.now()).strftime("%Y-%m-%d_%H-%M-%S")

INPUT_FOLDER="./input/"
DEF_DEV_CMD_FILE ="dev_cmd.json"
OUTPUT_FOLDER="./output/"
OUTPUT_FILE=OUTPUT_FOLDER+"Scan_summary-"+time1+".xlsx"
DEV_PORT="22"

print("*"*20 + "Enter credentials for devices " + "*" *20)
DEV_USERNAME=str(input("Device Username, or press ENTER for default[admin]:").strip() or "admin")
DEV_PASSWORD = pwinput.pwinput("Device Password:")
if not DEV_PASSWORD : print("Warning: Empty password entered")

print("*"*16 + " Enter the json file name with devices IP and cmds" + "*" *16)
DEV_CMD_FILE=str(input(f"File with IPs and cmds from folder {INPUT_FOLDER}, or press ENTER for default {DEF_DEV_CMD_FILE}:").strip() or DEF_DEV_CMD_FILE)
DEV_CMD_FILE=INPUT_FOLDER+DEV_CMD_FILE
if os.path.isfile(DEV_CMD_FILE):
    pass
else:  
    print(f"No such file: {DEV_CMD_FILE}")
    sys.exit()
with open(DEV_CMD_FILE, 'r') as devcmdfile:
        DEVCMDLIST = json.load(devcmdfile)

if not os.path.exists(OUTPUT_FOLDER):
      os.makedirs(OUTPUT_FOLDER)
      print("Output directory created successfully!")

print ("*"*15 + "start time - "+ time1 + "*" *15)
#logging.basicConfig(filename='netmiko_global.log', level=logging.DEBUG)
#logger = logging.getLogger("netmiko")

### geting one by one line from json file ##########     
for itemdev in DEVCMDLIST.keys():
    DEV_ADDRESS= DEVCMDLIST[itemdev]['IP']
    DEV = {
	"device_type" : "cisco_ios",
	"ip" : DEV_ADDRESS,
	"username" : DEV_USERNAME,
	"password" : DEV_PASSWORD,
    "port": DEV_PORT,
    "read_timeout_override": 100
    }
    CMDS= DEVCMDLIST[itemdev]['CMDS']
    LOCATION=DEVCMDLIST[itemdev]['LOCATION']
    ### start ssh sesion    
    print(DEV_ADDRESS," <-connecting") 
    try:
       with ConnectHandler(**DEV) as sshCli:    
            ### geting one by one cmd ##########      
            for itemcmd in CMDS.keys():
                cmd_output =  sshCli.send_command(CMDS[itemcmd]['CMD'], use_textfsm=True) 
                #cmd_output =  [ line for line in cmd_output.split('\n')]
                #pprint.pp(cmd_output)
                #print(json.dumps(cmd_output, indent=4))
                df=pd.json_normalize(cmd_output)
                df['device'] = itemdev
                df['location'] = LOCATION        
                try:          
                    dfexisting=pd.read_excel(OUTPUT_FILE, sheet_name=itemcmd)
                    df = pd.concat([dfexisting, df])
                    print("appending date to tab "+itemcmd+" from "+itemdev)
                #df=df.append(dfexisting, ignore_index=True,)
                except:
                    print("creating tab "+itemcmd+" for "+itemdev)
                
                try:          
                    writer = pd.ExcelWriter(OUTPUT_FILE, engine = 'openpyxl',mode="a",if_sheet_exists="replace")
                except:
                    writer = pd.ExcelWriter(OUTPUT_FILE, engine = 'openpyxl')
                df.to_excel(writer, index=False, sheet_name=itemcmd)
                writer.close()
                #print result in txt/json files
                #save_output = open("Output-"+itemdev+"-"+itemcmd+"-"+time1+".json", "w+")
                #save_output.write(json.dumps((cmd_output),indent=4))
                #save_output.close()

    except NetmikoAuthenticationException:
        print(f"Authentication Failed on {itemdev}")
        continue
    except NetmikoTimeoutException:
        print(f"Session timeout on {itemdev}")
        continue     
print ("*"*20 + " End " + "*" *20)