# CiscoIOS-Automation
get-csv-dev-cmd-to-txt.py script execut the same list of commands on many devices and allow filter results by words (eg.: Temperature, MAC, SN). The script read list of cmd and list of devices from csv file.

# Collecting info about Vendor of devices based on MAC address vendor list 
get-MAC-vendor.py - scripts script creates new tab MAC_vendor in Excel with sheet name 'mac' and columne name 'mac_address'.

# Endpoints inventory:
The following scripts collect endpoint's data from switches and other sources ( MACvendor, Infoblox). They create a flow where the next script is based on the data of the previous one
The scripts work on excel file in directory ./output/

1. get-json-dev-cmd-to-excel.py- script execut list of commands on many devices and merge the resulta in excel. The script read list of cmd and list of devices from json file. The script use netmiko, pandas, openpyxl python libriaries.

2. analyse-dev-cmd.py - script creates new tab with endpoints in Excel with sheets sh_mac, sh_cdp, sh_int, sh_arp containing collected from switches by get-json-dev-cmd-to-excel.py script. Default folder with Excel spredsheet ./output.

3. update-infoblox-date-to-excel.py - sends query to Infoblox API and collect info about DNS, DHCP configuration for found IP in Excel. The Excel spreadsheet should have sheets:endpoints, column:ip_address)

