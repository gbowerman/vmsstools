# Python script to upgrade a VM Scale Set one update domain at a time
# usage: vmssupgrade -r rgname -v vmssname -n newversion -u updatedomain [-y][--verbose][--nowait]
import azurerm
import getopt
import json
import sys
import time


def usage(message):
    print(message)
    print('usage: vmssupgrade -r rgname -v vmssname -n newversion -u updatedomain [-y][--verbose][--nowait]')
    sys.exit(2)


def main(argv):
    # switches to determine program behavior
    noprompt = False  # go ahead and upgrade without waiting for confirmation when True
    nowait = False  # don't loop waiting for upgrade provisioning to complete when True
    verbose = False  # print extra status information when True

    # evaluate command line arguments
    if (len(argv)) < 8:
        usage('Too few arguments.')
    try:
        opts, args = getopt.getopt(argv, 'yr:v:n:u:', ['resourcegroup=', 'vmssname=', 'newversion=', 'updatedomain='])
    except getopt.GetoptError:
        usage('Invalid argument.')
    for opt, arg in opts:
        if opt == '-y':
            noprompt = True
        elif opt == '--verbose':
            verbose = True
        elif opt == '--nowait':
            nowait = True
        elif opt in ("-r", "--resourcegroup"):
            resource_group = arg
        elif opt in ("-v", "--vmssname"):
            vmssname = arg
        elif opt in ("-n", "--newversion"):
            newversion = arg
        elif opt in ("-u", "--updatedomain"):
            updatedomain = arg

        # check everything got defined
        try:
            resource_group
        except NameError:
            usage('resourcegroup not defined')
        try:
            vmssname
        except NameError:
            usage('vmssname not defined')
        try:
            newversion
        except NameError:
            usage('newversion not defined')
        try:
            updatedomain
        except NameError:
            usage('updatedomain not defined')
    # hardcoded values for testing
    # make them arguments later
    # newversion = "14.04.201507060"

    # Load Azure app defaults
    try:
        with open('azurermconfig.json') as configFile:
            configdata = json.load(configFile)
    except FileNotFoundError:
        print("Error: Expecting vmssConfig.json in current folder")
        sys.exit()

    tenant_id = configdata['tenantId']
    app_id = configdata['appId']
    app_secret = configdata['appSecret']
    subscription_id = configdata['subscriptionId']
    # resource_group = configdata['resourceGroup']
    # vmssname = configdata['vmssName']

    access_token = azurerm.get_access_token(tenant_id, app_id, app_secret)

    # get the vmss model
    vmssmodel = azurerm.get_vmss(access_token, subscription_id, resource_group, vmssname)
    # print(json.dumps(vmssmodel, sort_keys=False, indent=2, separators=(',', ': ')))

    # check current version
    imagereference = vmssmodel['properties']['virtualMachineProfile']['storageProfile']['imagereference']
    print('Current image reference in Scale Set model:')
    print(json.dumps(imagereference, sort_keys=False, indent=2, separators=(',', ': ')))

    # compare current version with new version
    if imagereference['version'] == newversion:
        print('Scale Set model version is already set to ' + newversion + ', skipping model update.')
    else:
        if not noprompt:
            response = input('Confirm version upgrade to: ' + newversion + ' (y/n)')
            if response.lower() != 'y':
                sys.exit(1)
        # change the version
        vmssmodel['properties']['virtualMachineProfile']['storageProfile']['imagereference']['version'] = newversion

        # put the vmss model
        updateresult = azurerm.update_vmss(access_token, subscription_id, resource_group, vmssname,
                                           json.dumps(vmssmodel))
        if verbose:
            print(updateresult)
        print('OS version updated to ' + newversion + ' in model for VM Scale Set: ' + vmssname)

    # list the VMSS VM instance views to determine their update domains
    print("Examining the scale set..")
    instanceviewlist = azurerm.list_vmss_vm_instance_view(access_token, subscription_id, resource_group, vmssname)
    # print(json.dumps(instanceviewlist, sort_keys=False, indent=2, separators=(',', ': ')))

    # loop through the instance view list, and build the vm id list of VMs in the matching UD
    udinstancelist = []
    for instanceView in instanceviewlist['value']:
        vmud = instanceView['properties']['instanceView']['updatedomain']
        if str(vmud) == updatedomain:
            udinstancelist.append(instanceView['instanceId'])
    udinstancelist.sort()
    print('VM instances in UD: ' + str(updatedomain) + ' to upgrade:')
    print(udinstancelist)

    # do manualupgrade on the VMs in the list
    print('Upgrading VMs in UD: ' + str(updatedomain))
    upgraderesult = azurerm.upgrade_vmss_vms(access_token, subscription_id, resource_group, vmssname,
                                             json.dumps(udinstancelist))
    print(upgraderesult)

    # now wait for upgrade to complete
    # query VM scale set instance view
    if not nowait:
        updatecomplete = False
        while not updatecomplete:
            vmssinstanceview = azurerm.get_vmss_instance_view(access_token, subscription_id, resource_group, vmssname)
            for status in vmssinstanceview['statuses']:
                if status['code'] == 'ProvisioningState/succeeded':
                    updatecomplete = True
            if verbose:
                print(status['code'])
            time.sleep(5)
        print(status['code'])
    else:
        print('Check Scale Set provisioning state to determine when upgrade is complete.')


if __name__ == "__main__":
    main(sys.argv[1:])
