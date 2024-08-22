import sys
import pwinput
from netmiko import ConnectHandler
import csv
import json
import os
import time
import datetime
import logging
import pprint
time1 = (datetime.datetime.now()).strftime("%Y-%m-%d_%H-%M-%S")
DEV_PORT="22"
DEV_OUTPUT_SUM=""
OUTPUT_FOLDER="./output/"
CMDLIST_FILE = "./input/cmd.csv"
DEVLIST_FILE ="/input/dev.csv"
OUTPUT_FILE=OUTPUT_FOLDER +"CMD_summary_filted_cmd-"+ time1 + ".txt"
#get credentials
print("*"*20 + "Enter credentials for devices " + "*" *20)
DEV_USERNAME=str(input("Device Username, or press ENTER for default[admin]:").strip() or "admin")
DEV_PASSWORD = pwinput.pwinput("Device Password:")
if not DEV_PASSWORD : print("Warning: Empty password entered")
DEV_ENABLE = pwinput.pwinput("Device enable secret, or press ENTER for the same as password:")
if not DEV_ENABLE : DEV_ENABLE=DEV_PASSWORD
#get CMS's filename
print("*"*5 + " Enter the filename with list of cmds, filename with list of devices and filer" + "*" *5)
CMDLIST_FILE=str(input(f"CSV: enter the filename with list of commands, eg:[{CMDLIST_FILE}], or press ENTER for this default file:").strip() or CMDLIST_FILE)
if os.path.isfile(CMDLIST_FILE):
   with open(CMDLIST_FILE, 'r') as cmdfile:
      FIELDNAMES = ("CMD","DESCRIPTION")
      READER = csv.DictReader( cmdfile, FIELDNAMES )
      CMDLIST = json.loads(json.dumps([ row for row  in READER ], skipkeys=False ))
else:  
    print(f"No such file: {CMD_FILE} ")
    sys.exit()
#get DEVICES's filename
DEVLIST_FILE=str(input(f"CSV: enter the filename with list of devices, eg:[{DEVLIST_FILE}], or press ENTER for this default file]:").strip() or DEVLIST_FILE)
if os.path.isfile(DEVLIST_FILE):
   pass
else:  
    print(f"No such file: {DEVLIST_FILE} ")
    sys.exit()
#get FILTER
DEV_OUTPUTFILTER=str(input("Filter output for a particular word, or press ENTER for no filter:").strip() or " ")

#uncomment if you want log netmiko sesion
#logging 
#logging.basicConfig(filename='netmiko_global.log', level=logging.DEBUG)
#logger = logging.getLogger("netmiko")

#CREATING Ddirectory for output files
if not os.path.exists(OUTPUT_FOLDER):
      os.makedirs(OUTPUT_FOLDER)
      print("Output directory created successfully!")

#############################Start session#################################
print ("*"*18 + "start time - "+ time1 + "*" *18)       
with open(DEVLIST_FILE) as file:   
  for item in file:
   DEV_ADDRESS = item.strip("\n") 
   print(DEV_ADDRESS," <-connecting")
   DEV_OUTPUT_SUM += DEV_ADDRESS+"::\n"
   DEV = {
	"device_type" : "cisco_ios",
	"ip" : DEV_ADDRESS,
	"username" : DEV_USERNAME,
	"password" : DEV_PASSWORD,
   "secret" : DEV_ENABLE,
   "port": DEV_PORT,
   "read_timeout_override": 90
   }
   itemcmd={}
   with ConnectHandler(**DEV) as sshCli:
      sshCli.enable()
      iterCMD = iter(CMDLIST)
      next(iterCMD)
      for itemcmd in iterCMD:  
         DEV_OUTPUT =  sshCli.send_command(itemcmd["CMD"])
         DEV_OUTPUT_FILTERED=filter(DEV_OUTPUT, DEV_OUTPUTFILTER)
         DEV_OUTPUT_FILTERED =  [ line for line in DEV_OUTPUT.split('\n') if DEV_OUTPUTFILTER in line]
         pprint.pp(DEV_OUTPUT_FILTERED)
         DEV_OUTPUT_SUM += str(DEV_OUTPUT_FILTERED)+"\n"
#uncomment if you want save not filtered results
# You can add DESCRIPTION of cmd's action to the output filename 
#         save_output = open(OUTPUT_FOLDER+ DEV_ADDRESS + "-"+ itemcmd["DESCRIPTION"] + "-"+ time1 + ".txt", "w+")
#         save_output.write(DEV_OUTPUT)
#         save_output.close()   

save_output_sum = open(OUTPUT_FILE, "w+")
save_output_sum.write(DEV_OUTPUT_SUM)
save_output_sum.close() 
print ("*"*24 + " End " + "*" *24)