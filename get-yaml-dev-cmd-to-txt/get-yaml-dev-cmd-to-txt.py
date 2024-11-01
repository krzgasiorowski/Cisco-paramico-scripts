import sys
import pwinput
from netmiko import ConnectHandler
from netmiko import NetmikoAuthenticationException
from netmiko import NetmikoTimeoutException
from ntc_templates.parse import parse_output
import os
import time
import datetime
import pprint
import yaml
import logging
time1 = (datetime.datetime.now()).strftime("%Y-%m-%d_%H-%M-%S")
DEV_OUTPUT_SUM=""
OUTPUT_FOLDER="./output/"
INPUT_FOLDER = "./input/"

#get credentials
print("*"*20 + "Enter credentials for devices " + "*" *20)
DEV_USERNAME=str(input("Device Username, or press ENTER for default[admin]:").strip() or "admin")
DEV_PASSWORD = pwinput.pwinput("Device Password:")
if not DEV_PASSWORD : print("Warning: Empty password entered")
DEV_ENABLE = pwinput.pwinput("Device enable secret, or press ENTER for the same as password:")
if not DEV_ENABLE : DEV_ENABLE=DEV_PASSWORD

CON_INFO = {
    'ip' :'',
    'device_type' : 'cisco_ios',
    'username' : DEV_USERNAME,
    'password' : DEV_PASSWORD,
    'secret' : DEV_ENABLE,
    'port' : '22',
    'read_timeout_override': 90,
    "global_delay_factor": 2,
}

#get DevIP & CMD file
DEV_CMD_FILE_NAME=str(input(f"Enter the yaml filename with list of commands and devices IP's:  {INPUT_FOLDER}"))
if os.path.isfile(INPUT_FOLDER+DEV_CMD_FILE_NAME):
   with open(INPUT_FOLDER+DEV_CMD_FILE_NAME, 'r') as f:
      DEV_CMD = yaml.safe_load(f)
else:  
    print(f"No such file: {DEV_CMD_FILE_NAME} ")
    sys.exit()
     
# Print for troublehoting
#pprint.pprint(DEV_CMD)
#print(DEV_CMD.get("TASKS")[0]["TASK1"]["DEVGROUP"])
#print(DEV_CMD.get("TASKS")[0]["TASK1"]["CMDSET"])
#print(DEV_CMD["DEVS"]["DEVGROUP1"][0]["IP"])
#print(DEV_CMD["DEVS"]["DEVGROUP1"][0]["HOSTNAME"])
#print((DEV_CMD["DEVS"]["DEVGROUP1"][2]).get("HOSTNAME"))
#print(DEV_CMD["CMDS"]["CMDSET1"][0]["CMD"])

#uncomment if you want log netmiko sesion
#logging 
#logging.basicConfig(filename='netmiko_global.log', level=logging.DEBUG)
#logger = logging.getLogger("netmiko")

OUTPUT_FILE=OUTPUT_FOLDER +"Output-"+DEV_CMD_FILE_NAME+"-"+ time1 + ".txt"
#CREATING Ddirectory for output files
if not os.path.exists(OUTPUT_FOLDER):
      os.makedirs(OUTPUT_FOLDER)
      print("Output directory created successfully!")

############# Start loops ##################

for item in (DEV_CMD.get("TASKS")): # Getting list of TASKS
    DEVGROUP=str(item.get("DEVGROUP"))
    CMDSET=item.get("CMDSET")
    print ("*"*20 +"Task for "+ DEVGROUP +" and " + CMDSET+"*"*20)
    
    for itemdev in (DEV_CMD["DEVS"][DEVGROUP]): # Finding DEVICES in DEVGROUP specified in TASK
        if itemdev.get('HOSTNAME')==None: itemdev["HOSTNAME"]=itemdev["IP"]
        print(itemdev['HOSTNAME']," <-connecting")
        CON_INFO['ip']=itemdev["IP"]
        try:
            with ConnectHandler(**CON_INFO) as sshCli:
                sshCli.enable()
                
                for itemcmd in (DEV_CMD["CMDS"][CMDSET]) or []: # Getting list of COMMANDS in CMDSET specified in TASK, skip empty list
                        CMD=itemcmd["CMD"]
                        if itemcmd['CONFIG-MODE']==True:
                            DEV_OUTPUT =  sshCli.send_config_set(CMD) # Send Commands in CONFIG MODE
                            if itemcmd['SAVE-CONF']==True: DEV_OUTPUT += sshCli.save_config() #Save Config 
                        else: 
                            DEV_OUTPUT =  sshCli.send_command(CMD, use_textfsm=False) # Send Commands in ENABLE MODE

                        if itemcmd["SAVE-CMD-OUTPUT-TO-FILE"]==True: # Save output to file or print on the screen                      
                            save_output = open(OUTPUT_FOLDER+ itemdev["HOSTNAME"] + "-"+ itemcmd["CMD-OUTPUT-DESCRIPTION"] + "-"+ time1 + ".txt", "w+")
                            save_output.write(DEV_OUTPUT)
                            save_output.close()
                            print (f"{CMD} output saved to file")
                        else:
                            pprint.pp(DEV_OUTPUT)
        except NetmikoAuthenticationException:
            print(f"Authentication Failed on {itemdev}")
            continue
        except NetmikoTimeoutException:
            print(f"Session timeout on {itemdev}")
            continue     