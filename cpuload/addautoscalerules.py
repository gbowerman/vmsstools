# addautoscalerules.py - example program to add autoscale rules to a VM scale set
# in this example the resource group, scale set, and rules are hardcoded
# to do: make this into a generic program to turn a regular scale set into an autoscale scale set
import json
import azurerm

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

# hardcode vmss parameters for now
rgname = 'sgelastic'
vmssname = 'sgelastic'   

# authenticate
access_token = azurerm.get_access_token(tenant_id, app_id, app_secret)

# figure out location
try:
    rg = azurerm.get_resource_group(access_token, subscription_id, rgname)
    location = rg['location']
except KeyError:
    print('Cannot find resource group ' + rgname + '. Check connection/authorization.')
    print(json.dumps(rg, sort_keys=False, indent=2, separators=(',', ': ')))
    sys.exit()
print('location = ' + location)

# create autoscale rule
print('Creating autoscale rules')
metric_name = 'Percentage CPU'
operator = 'GreaterThan'
threshold = 60
direction = 'Increase'
change_count = 1
rule1 = azurerm.create_autoscale_rule(subscription_id, rgname, vmssname, metric_name, operator, \
    threshold, direction, change_count)
threshold = 10
operator = 'LessThan'
direction = 'Decrease'
rule2 = azurerm.create_autoscale_rule(subscription_id, rgname, vmssname, metric_name, operator, \
    threshold, direction, change_count)
rules = [rule1, rule2]
# print(json.dumps(rules, sort_keys=False, indent=2, separators=(',', ': ')))

# create autoscale setting
setting_name = "SGELASTIC autoscale settings"
print('Creating autoscale setting: ' + setting_name)
min = 999
max = 1000
default = 1000
response = azurerm.create_autoscale_setting(access_token, subscription_id, rgname, setting_name, \
    vmssname, location, min, max, default, rules)
if response.status_code != 201:
    print("Autoscale setting create error: " + str(response.status_code))
else:
    print("Autoscale settings created.")
