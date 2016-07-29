# Python script to do read/install/delete VM extensions on VM Scale Sets
# usage: vmssextn -r rgname -v vmssname [--delete extnname] [--add extnfile] [-y][--verbose]

import argparse
import json
import sys
import time

import subscription
import vmss
import azurerm


def main():
    # create parser
    argParser = argparse.ArgumentParser()

    argParser.add_argument('--vmssname', '-s', required=True, action='store', help='VM Scale Set name')
    argParser.add_argument('--resourcegroup', '-r', required=True, dest='resource_group', action='store',
                           help='Resource group name')
    argParser.add_argument('--delete', '-n', dest='extnname', action='store', help='Name of extension to delete')
    argParser.add_argument('--add', '-c', dest='extnfile', action='store',
                           help='File containing extension defintion to add')
    argParser.add_argument('--verbose', '-v', action='store_true', default=False, help='Show additional information')
    argParser.add_argument('-y', dest='noprompt', action='store_true', default=False,
                           help='Do not prompt for confirmation')

    args = argParser.parse_args()

    # switches to determine program behavior
    noprompt = args.noprompt  # go ahead and upgrade without waiting for confirmation when True
    verbose = args.verbose  # print extra status information when True
    vmssname = args.vmssname
    resource_group = args.resource_group
    if args.extnname is not None:
        extnname = args.extnname
        mode = 'delete'
    elif args.extnfile is not None:
        extnfile = args.extnfile
        mode = 'add'
    else:
        mode = 'report'

    # Load Azure app defaults
    try:
        with open('vmssconfig.json') as configFile:
            configData = json.load(configFile)
    except FileNotFoundError:
        print("Error: Expecting vmssconfig.json in current folder")
        sys.exit()

    sub = subscription.subscription(configData['tenantId'], configData['appId'], configData['appSecret'],
                                    configData['subscriptionId'])
    sub.get_vmss_list()
    current_vmss = vmss.vmss(vmssname, sub.vmssdict[vmssname], sub.sub_id, sub.access_token)
    # print(json.dumps(vmssmodel, sort_keys=False, indent=2, separators=(',', ': ')))

    # start by getting the extension list
    try:
        extnprofile = current_vmss.model['properties']['virtualMachineProfile']['extensionProfile']
    except KeyError:
        if mode != 'add':
            print('Scale Set: ' + vmssname + ' does not have any extensions defined.')
            sys.exit()
        else:
            extnprofile = None

    if mode == 'report':
        # print selected details about each extension
        print('Found the following extensions in scale set: ' + vmssname)

        for extension in extnprofile['extensions']:
            print('\nName: ' + extension['name'])
            print('Type: ' + extension['properties']['type'])
            print('Publisher: ' + extension['properties']['publisher'])
            print('Version: ' + extension['properties']['typeHandlerVersion'])
            if verbose:
                print(json.dumps(extension, sort_keys=False, indent=2, separators=(',', ': ')))
        sys.exit()

    elif mode == 'delete':
        index = 0
        extn_index = -1
        for extension in extnprofile['extensions']:
            if extension['name'] == extnname:
                extn_index = index
            index += 1
        if extn_index > -1:
            # delete the extension from the list
            del extnprofile['extensions'][extn_index]
        else:
            print('Extension ' + extnname + ' not found.')

    elif mode == 'add':
        # load the extension definition file
        try:
            with open(extnfile) as extension_file:
                extndata = json.load(extension_file)
        except FileNotFoundError:
            print("Error: Expecting ' + extnfile + ' in current folder (or absolute path)")
            sys.exit()

        if extnprofile is None:
            # create an extensionProfile
            extnprofile = {'extensions':[]}
        # add the extension definition to the list
        extnprofile['extensions'].append(extndata)

    # update and apply model with the new extensionProfile
    current_vmss.update_extns(extnprofile)
    print('VMSS update status: ' + str(current_vmss.status.status_code))
    if current_vmss.status.status_code == 200:
        if current_vmss.upgradepolicy == 'Manual':
            print('Update in progress. Once model update completes, apply manualUpgrade to VMs.')
            print("Note: You won't be able re-add an extension of the same name until the new model is applied to all VMs.")
        else:
            print('Scale Set update in progress.')
    else:
        print(current_vmss.status.text)
if __name__ == "__main__":
    main()
