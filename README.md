# CiscoIOS-Automation
get-csv-dev-cmd-to-txt.py script execut the same list of commands on many devices and allow filter results by words (eg.: Temperature, MAC, SN). The script read list of cmd and list of devices from csv file.

get-json-dev-cmd-to-excel.py- script execut list of commands on many devices and merge the resulta in excel. The script read list of cmd and list of devices from json file. The script use netmiko, pandas, openpyxl python libriaries.

analyse-dev-cmd.py - script creates new tab with endpoints in Excel with sheets sh_mac, sh_cdp, sh_int, sh_arp containing collected from switches by get-json-dev-cmd-to-excel.py script. Default folder with Excel spredsheet ./output.

get-MAC-vendor.py - scripts script creates new tab MAC_vendor in Excel with sheet name 'mac' and columne name 'mac_address'.
