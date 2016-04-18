# Python script to upgrade a VM Scale Set one update domain at a time
# usage: vmssupgrade -r rgname -v vmssname -n newversion -u updatedomain [-y][--verbose][--nowait]
# test values for ubuntu 14.04 platform image:
#   oldversion = "14.04.201506100"
#   newversion = "14.04.201507060"
import azurerm
import getopt
import json
import sys
import time


def usage(message):
    print(message)
    print('usage: vmssupgrade -r rgname -s vmssname -n newversion {-u updatedomain|-i vmid|-l vmlist} [-y][-v][-h]')
    print('-r, --resourcegroup <resource group name> ')
    print('-s, --vmssname <scale set name> ')
    print('-n, --newversion <new version>')
    print('-u --updatedomain <update domain> | -i <vm id> | -l <vm list>')
    sys.exit(2)


def main(argv):
    # switches to determine program behavior
    noprompt = False             # go ahead and upgrade without waiting for confirmation when True
    nowait = False               # don't loop waiting for upgrade provisioning to complete when True
    verbose = False              # print extra status information when True
    upgrademode = 'updatedomain'  # determines whether to upgrade by domain, vmlist, or single vm

    # evaluate command line arguments
    if (len(argv)) < 8:
        usage('Too few arguments.')
    try:
        opts, args = getopt.getopt(argv, 'yvr:s:n:u:i:l:', ['resourcegroup=', 'vmssname=', 'newversion=', 'updatedomain=', 'vmid=', 'vmlist='])
    except getopt.GetoptError as err:
        usage(err)
    for opt, arg in opts:
        if opt == '-y':
            noprompt = True
        elif opt in ['-v', '--verbose']:
            verbose = True
        elif opt in ['-n', '--nowait']:
            nowait = True
        elif opt in ['-s', '--vmssname']:
            vmssname = arg
        elif opt in ['-r', '--resourcegroup']:
            resource_group = arg
        elif opt in ['-n', '--newversion']:
            newversion = arg
        elif opt in ['-u', '--updatedomain']:
            updatedomain = arg
            upgrademode = 'updatedomain'
        elif opt in ['-i', '--vmid']:
            vmid = arg
            upgrademode = 'vmid'
        elif opt in ['-l', '--vmlist']:
            vmlist = arg
            upgrademode = 'vmlist'

    # check the required arguments were provided
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
        try:
            vmid
        except NameError:
            try:
                vmlist
            except NameError:
                usage('You must specify an update domain, a vm id, or a vm list')

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
    imagereference = vmssmodel['properties']['virtualMachineProfile']['storageProfile']['imageReference']
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
        vmssmodel['properties']['virtualMachineProfile']['storageProfile']['imageReference']['version'] = newversion

        # put the vmss model
        updateresult = azurerm.update_vmss(access_token, subscription_id, resource_group, vmssname,
                                           json.dumps(vmssmodel))
        if verbose:
            print(updateresult)
        print('OS version updated to ' + newversion + ' in model for VM Scale Set: ' + vmssname)

    # build the list of VMs to upgrade depending on the upgrademode setting
    if upgrademode == 'updatedomain':
        # list the VMSS VM instance views to determine their update domains
        print("Examining the scale set..")
        instanceviewlist = azurerm.list_vmss_vm_instance_view(access_token, subscription_id, resource_group, vmssname)
        # print(json.dumps(instanceviewlist, sort_keys=False, indent=2, separators=(',', ': ')))

        # loop through the instance view list, and build the vm id list of VMs in the matching UD
        udinstancelist = []
        for instanceView in instanceviewlist['value']:
            vmud = instanceView['properties']['instanceView']['platformUpdateDomain']
            if str(vmud) == updatedomain:
                udinstancelist.append(instanceView['instanceId'])
        udinstancelist.sort()
        print('VM instances in UD: ' + str(updatedomain) + ' to upgrade:')
        print(udinstancelist)
        vmids = json.dumps(udinstancelist)
        print('Upgrading VMs in UD: ' + str(updatedomain))
    elif upgrademode == 'vmid':
        vmids = json.dumps([str(vmid)])
        print('Upgrading VM ID: ' + str(vmid))
    else:  # upgrademode = vmlist
        vmids = vmlist
        print('Upgrading VM IDs: ' + vmlist)

    # do manualupgrade on the VMs in the list

    upgraderesult = azurerm.upgrade_vmss_vms(access_token, subscription_id, resource_group, vmssname, vmids)
    print(upgraderesult)

    # now wait for upgrade to complete
    # query VM scale set instance view
    if not nowait:
        updatecomplete = False
        provisioningstate = ''
        while not updatecomplete:
            vmssinstanceview = azurerm.get_vmss_instance_view(access_token, subscription_id, resource_group, vmssname)
            for status in vmssinstanceview['statuses']:
                provisioningstate = status['code']
                if provisioningstate == 'ProvisioningState/succeeded':
                    updatecomplete = True
            if verbose:
                print(provisioningstate)
            time.sleep(5)
        print(status['code'])
    else:
        print('Check Scale Set provisioning state to determine when upgrade is complete.')


if __name__ == "__main__":
    main(sys.argv[1:])
