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
output_folder="./output/"
input_folder = "./input/"

#get credentials
print("*"*20 + "Enter credentials for devices " + "*" *20)
dev_username=str(input("Device Username, or press ENTER for default[admin]:").strip() or "admin")
dev_password = pwinput.pwinput("Device Password:")
if not dev_password : print("Warning: Empty password entered")
dev_enable = pwinput.pwinput("Device enable secret, or press ENTER for the same as password:")
if not dev_enable : dev_enable=dev_password

connect_info = {
    'ip' :'',
    'device_type' : 'cisco_ios',
    'username' : dev_username,
    'password' : dev_password,
    'secret' : dev_enable,
    'port' : '22',
    #'read_timeout_override': 60,
    #"global_delay_factor": 0.1,
    "fast_cli": True,
}

#get DevIP & CMD file
tasks_dic_filename=str(input(f"Enter the yaml filename with list of commands and devices IP's:  {input_folder}"))
if os.path.isfile(input_folder+tasks_dic_filename):
   with open(input_folder+tasks_dic_filename, 'r') as inputfile:
      tasks_dic = yaml.safe_load(inputfile)
else:  
    print(f"No such file: {tasks_dic_filename} ")
    sys.exit()
out_summary_filename="out_" + tasks_dic_filename + "-"+ time1 + ".txt"
out_summary=""     
# Print for troublehoting
#pprint.pprint(tasks_dic)
#print(tasks_dic.get("TASKS")[0]["TASK1"]["DEVGROUP"])
#print(tasks_dic.get("TASKS")[0]["TASK1"]["CMDSET"])
#print(tasks_dic["DEVS"]["DEVGROUP1"][0]["IP"])
#print(tasks_dic["DEVS"]["DEVGROUP1"][0]["HOSTNAME"])
#print((tasks_dic["DEVS"]["DEVGROUP1"][2]).get("HOSTNAME"))
#print(tasks_dic["CMDS"]["CMDSET1"][0]["CMD"])

#uncomment if you want log netmiko sesion
#logging 
#logging.basicConfig(filename='netmiko_global.log', level=logging.DEBUG)
#logger = logging.getLogger("netmiko")

#CREATING Directory for output files
if not os.path.exists(output_folder):
      os.makedirs(output_folder)
      print("Output directory created successfully!")

############# Start reading tasks file ##################
for itemtask in (tasks_dic.get("TASKS")): # Getting TASKS as list
    devgroup_selected=itemtask['DEVGROUP']
    cmdset_selected=itemtask['CMDSET']
    print (f"Task for {devgroup_selected} and {cmdset_selected}")
    
    for itemdev in (tasks_dic["DEVS"][devgroup_selected]): # Getting DEVICES in DEVGROUP specified in TASK as list
        if itemdev.get('HOSTNAME')==None: itemdev["HOSTNAME"]=itemdev["IP"]
        print(itemdev['HOSTNAME']," <-connecting")
        out_summary+="\n"+itemdev['HOSTNAME']+">>>>\n"
        connect_info['ip']=itemdev["IP"]
        try:
            with ConnectHandler(**connect_info) as sshCli:
                sshCli.enable()
                
                for itemcmd in (tasks_dic["CMDS"][cmdset_selected]) or []: # Getting COMMANDS in CMDSET specified in TASK as list, skip empty list
                        CMD=itemcmd["CMD"]
                        if itemcmd['CONFIG-MODE']==True:
                            dev_output =  sshCli.send_config_set(CMD) # Send Commands in CONFIG MODE
                            if itemcmd['SAVE-CONF']==True: dev_output += sshCli.save_config() #Save Config 
                        else: 
                            dev_output =  sshCli.send_command(CMD, use_textfsm=False) # Send Commands in ENABLE MODE

                        if itemcmd["SAVE-CMD-OUTPUT-TO-FILE"]==True: # Save output to file or print on the screen                      
                            with open (output_folder + itemdev["HOSTNAME"] + "-"+ itemcmd["CMD-OUTPUT-DESCRIPTION"] + "-"+ time1 + ".txt",'w') as fileout:
                                       fileout.write(dev_output)
                            print (f"<{CMD}> output saved to file")
                            out_summary+="<"+CMD+"> output saved to file\n"
                        else:
                            pprint.pp(dev_output)
                            out_summary+=dev_output+"\n"
        except NetmikoAuthenticationException:
            print(f"Authentication Failed on {itemdev}")
            continue
        except NetmikoTimeoutException:
            print(f"Session timeout on {itemdev}")
            continue
#with open (output_folder + out_summary_filename,'w') as fsumout: #save summary to file if you wish
#    fsumout.write(out_summary)
#print (f"Summary of tasks has been saved in file {output_folder + out_summary_filename}")     