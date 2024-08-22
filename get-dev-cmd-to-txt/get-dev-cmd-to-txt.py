import sys
import pwinput
from netmiko import ConnectHandler
import json
import os
import time
import datetime
import logging
import pprint
time1 = (datetime.datetime.now()).strftime("%Y-%m-%d_%H-%M-%S")

print("*"*20 + "Enter credentials for devices " + "*" *20)
DEV_USERNAME=str(input("Device Username, or press ENTER for default[admin]:").strip() or "admin")
DEV_PASSWORD = pwinput.pwinput("Device Password:")
if not DEV_PASSWORD : print("Warning: Empty password entered")
DEV_ENABLE = pwinput.pwinput("Device enable secret, or press ENTER for the same as password:")
#DEV_ENABLE=str(input("Device enable secret, or press ENTER for the same as password:").strip())
if not DEV_ENABLE : DEV_ENABLE=DEV_PASSWORD
DEV_PORT="22"
DEV_OUTPUT_SUM=""

OUTPUT_FOLDER="./output/"
OUTPUT_FILE="CMD_summary_filted_cmd-"+ time1 + ".txt"
INPUT_FOLDER="./input/"
CMD_FILE = "cmd.json"
DEVICES_FILE ="devices.csv"

print("*"*5 + " Enter one command to execute on each devices, filename with devices and filer or allow read its from file " + "*" *5)
CMD=str(input(f"CMD: enter the one commmand, or press ENTER for load from file {INPUT_FOLDER}{CMD_FILE}:").strip())
if CMD=="" :
   if os.path.isfile(INPUT_FOLDER+CMD_FILE):
      with open(INPUT_FOLDER+CMD_FILE, 'r') as cmdfile:
        CMDLIST = json.load(cmdfile)
#      pass
   else:  
       print(f"No such file: {CMD_FILE} in  directory {INPUT_FOLDER}")
       sys.exit()
else:
   CMDLIST = {"enterd cmd": {"CMD": CMD}}
DEVLIST_FILE=str(input(f"CSV: enter the filename with list of devices, or press ENTER for default file[{INPUT_FOLDER}{DEVICES_FILE}]:").strip() or INPUT_FOLDER+DEVICES_FILE)
if os.path.isfile(DEVLIST_FILE):
   pass
else:  
    print(f"No such file: {DEVLIST_FILE} ")
    sys.exit()
DEV_OUTPUTFILTER=str(input("Filter output for a particular word, or press ENTER for no filter:").strip() or " ")

#Time variable2
time2 = (datetime.datetime.now()).strftime("%Y-%m-%d_%H-%M-%S")

#logging 
#logging.basicConfig(filename='netmiko_global.log', level=logging.DEBUG)
#logger = logging.getLogger("netmiko")

if not os.path.exists(OUTPUT_FOLDER):
      os.makedirs(OUTPUT_FOLDER)
      print("Output directory created successfully!")
###############Start session#############       
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
   with ConnectHandler(**DEV) as sshCli:
      sshCli.enable()
      for itemcmd in CMDLIST.keys():
         DEV_OUTPUT =  sshCli.send_command(CMDLIST[itemcmd]['CMD'])
         DEV_OUTPUT_FILTERED=filter(DEV_OUTPUT, DEV_OUTPUTFILTER)
         DEV_OUTPUT_FILTERED =  [ line for line in DEV_OUTPUT.split('\n') if DEV_OUTPUTFILTER in line]
         pprint.pp(DEV_OUTPUT_FILTERED)
#         print(DEV_OUTPUT_FILTERED))
         DEV_OUTPUT_SUM += str(DEV_OUTPUT_FILTERED)+"\n"
#save not filtered
         save_output = open(OUTPUT_FOLDER + DEV_ADDRESS + "-"+ itemcmd + "-"+ time1 + ".txt", "w+")
         save_output.write(DEV_OUTPUT)
         save_output.close()   

save_output_sum = open(OUTPUT_FOLDER+OUTPUT_FILE, "w+")
save_output_sum.write(DEV_OUTPUT_SUM)
save_output_sum.close() 
print ("*"*20 + " End " + "*" *20)