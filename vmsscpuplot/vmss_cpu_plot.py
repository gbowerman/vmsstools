# vmss_cpu_plot.py
# - prints most recent CPU host metrics for the named scale set
# To use this program without modification you need vmssconfig.json 
#  in the local folder containing:
#  - tenant id
#  - application id
#  - application secret
#  - subscription id 
import argparse
import azurerm
import datetime
import json
import matplotlib.pyplot as pyplot
import matplotlib.dates as dates
import sys

def main():
    # create argument parser
    argParser = argparse.ArgumentParser()

    argParser.add_argument('--vmss', '-n', required=True, action='store', \
        help='Scale set name')
    argParser.add_argument('--resourcegroup', '-g', required=True, dest='resource_group', \
        action='store', help='Resource group name')
    argParser.add_argument('--verbose', '-v', action='store_true', default=False, \
        help='Print verbose metrics output to console')

    args = argParser.parse_args()

    verbose = args.verbose  # dump metrics JSON output to console when True
    vmssname = args.vmss
    rgname = args.resource_group

    # Load Azure app defaults
    try:
        with open('azurermconfig.json') as configFile:    
            configData = json.load(configFile)
    except FileNotFoundError:
        print("Error: Expecting azurermonfig.json in current folder")
        sys.exit()
    
    tenant_id = configData['tenantId']
    app_id = configData['appId']
    app_secret = configData['appSecret']
    subscription_id = configData['subscriptionId']

    # get Azure access token
    access_token = azurerm.get_access_token(tenant_id, app_id, app_secret)

    # get host metrics for the named VM scale set
    provider = 'Microsoft.Compute'
    resource_type = 'virtualMachineScaleSets'
    metrics = azurerm.get_metrics_for_resource(access_token, subscription_id, rgname, \
        provider, resource_type, vmssname)
    if verbose == True:
        print(json.dumps(metrics, sort_keys=False, indent=2, separators=(',', ': ')))

    # sort metrics into CPU and timestamp lists for easy plotting
    for metric in metrics['value']:
        if metric['name']['value'] == 'Percentage CPU':
            timestamp_list = []
            cpu_list = []
            for data in metric['data']:
                if 'average' in data:
                    cpu_list.append(data['average'])
                    # convert timestamp from 2016-11-26T06:26:00Z to python datetime format
                    dt = datetime.datetime.strptime(data['timeStamp'], '%Y-%m-%dT%H:%M:%SZ')
                    timestamp_list.append(dt)
            break

    # set figure title and graph style
    fig = pyplot.gcf()
    fig.canvas.set_window_title('Host metrics graph')
    #ig.patch.set_facecolor('white')
    pyplot.style.use('ggplot')
    #ax = pyplot.gca()
    #ax.set_axis_bgcolor('grey')

    # plot values
    pyplot.plot(timestamp_list, cpu_list)
    pyplot.gcf().autofmt_xdate()
    pyplot.ylim([0,100])

    # label axis and graph
    pyplot.ylabel('CPU Percentage')
    pyplot.xlabel('Time stamp (UTC)')
    pyplot.title('Avg CPU over time for scale set: ' + vmssname)

    # display
    pyplot.show()

if __name__ == "__main__":
    main()
