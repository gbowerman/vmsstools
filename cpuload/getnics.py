# getnics.py - script to get the internal IP addresses from the VMs in a scale set
# to do: do not hardcode the rgname and vmssname - instead make them command line
#  parameters
import azurerm
import json

# Load Azure app defaults
try:
   with open('azurermconfig.json') as configFile:
      configData = json.load(configFile)
except FileNotFoundError:
   print("Error: Expecting azurermconfig.json in current folder")
   sys.exit()

tenant_id = configData['tenantId']
app_id = configData['appId']
app_secret = configData['appSecret']
subscription_id = configData['subscriptionId']
rgname = 'sgelastic'
vmssname = 'sgelastic'

# authenticate
access_token = azurerm.get_access_token(tenant_id, app_id, app_secret)

nics = azurerm.get_vmss_nics(access_token, subscription_id, rgname, vmssname)
for nic in nics['value']:
    #print(json.dumps(nic, sort_keys=False, indent=2, separators=(',', ': ')))
    ipaddress = nic['properties']['ipConfigurations'][0]['properties']['privateIPAddress']
    print(ipaddress)