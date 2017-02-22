# vmsstools
Azure VM Scale Set scripts. Use at your own risk :-)

## jumpbox

Creates a new VM in a resource group. You can use this to create a VM in an empty resource group if you want, or use it to create a jump box in an existing VNET to be used to connect to existing resources in the VNET like VM scale set VMs.

```
usage: jumpbox.py [-h] --vmname VMNAME --rgname RGNAME [--user USER]
                  [--password PASSWORD] [--sshkey SSHKEY] [--sshpath SSHPATH]
                  [--location LOCATION] [--dns DNS] [--vnet VNET] [--nowait]
                  [--nonsg] [--verbose]
                  
The following arguments are required: --vmname/-n, --rgname/-g
```

This tool will create a VM in the first VNET it finds in the resource group (or the VNET you specify). If it doesn't find a VNET it will create one.

You can provide a user and password/public key/public key file. If no authentication method provided and no default public key file found it will create a password for you.

By default jumpbox.py will wait for the VM to be provisioned, unless you specify the --nowait argument.

![jumpbox screenshot](./docs/jumpbox.png)

## vipswap

Swaps the public IP addresses between two Azure load balancers.

```
usage: vip_swap.py [-h] --resourcegroup RESOURCE_GROUP --lb1 LB1 --lb2 LB2
                   [--verbose] [-y]
The following arguments are required: --resourcegroup/-g, --lb1/-1, --lb2/-2
```

![vipswap screenshot](../docs/vipswap.png)


## cpuload -  Random load generator for Azure VM scale set VMs
A set of scripts to trigger a randmon CPU load against  the VMs in a scale set. Tested up to 1000 VMs.

To generate a load:
1. Deploy a VM scale set which includes a custom script extension which deploys a Python bottle server: [https://github.com/gbowerman/azure-myriad/blob/master/bigtest/bigbottle.json](https://github.com/gbowerman/azure-myriad/blob/master/bigtest/bigbottle.json)
2. Deploy a jumpbox VM in the same subnet. E.g. use [https://github.com/gbowerman/vmsstools/tree/master/jumpbox](https://github.com/gbowerman/vmsstools/tree/master/jumpbox)
3. ssh to the jumpbox VM and use the getnics.py script to generate a list of VMSS VMs. Note: this requires an _azurermconfig.json_ file in the same directory which contains your service principal app/tenant details and subscription id.
   ```bash
   python3 getnics.py > ipaddrs
   ```
4. Edit random-load.py to set your resource group name and scale set name.
5. start a load running in background with:
   ```bash
   nohup python3 random-load.py > random.out 2>&1 &
   ```
6. kill the process when you're done.

## vmss_cpu_plot

Shows CPU usage graph for a VM scale set.

![CPU graph screenshot](./docs/cpu_graph.png)

Usage: vmss_cpu_plot.py [-h] --vmss VMSS --resourcegroup RESOURCE_GROUP [--verbose]

Graphs CPU usage for the named scale set for the last hour.


## vmssextn

Tool to read, add, remove extensions from an Azure VM Scale Set.

![vmssextn screenshot](./docs/vmssextn_show.png)

This script can:

  1. Show the extensions which are installed in a Virtual Machine Scale Set.
  2. Delete an extension from a VM Scale Set by name.
  3. Add an extension to a VM Scale Set by providing a JSON file containing the properties.
  
Note: this tool just updates the VMSS model. After that, if the VMSS 'upgradePolicy' property is set to 'Manual', you will have to call manualUgrade on the VMs to apply the update.

### Showing which extensions are installed

Lists the extensions installed in a specified scale set, including name, publisher, version. 

Use –verbose to dump the JSON properties, which could then be saved to a file and used to add extensions to other scale sets.

E.g. python vmssextn.py --resourcegroup extntest --vmssname extntest

### Adding 

Add an extension to a VM Scale Set by specifying a file containing an extension definition in JSON format.

E.g. python vmssextn.py --resourcegroup extntest --vmssname extntest --add extnfile

For an example JSON extension definition file to add, see: [lapextension.json](./lapextension.json)

Note: this tool just updates the VMSS model. After that, if the VMSS the 'upgradePolicy' property is set to 'Manual', you will have to call manualUgrade on the VMs to apply the update.

### Deleting an extension

Delete a VM extension from a VM Scale Set by name.

E.g. python vmssextn.py --resourcegroup extntest --vmssname extntest --delete extnname

Note: this tool just updates the VMSS model. After that, if the VMSS 'upgradePolicy' property is set to 'Manual', you will have to call manualUgrade on the VMs to apply the update.

### Updating an extension

Updates a VM extension from a VM Scale Set by name using a JSON definition in a file.

E.g. python vmssextn.py --resourcegroup extntest --vmssname extntest --update extnfile 

  
## vmssupgrade

Tool to roll out an OS upgrade to a running VM Scale Set, one upgrade domain at a time. 

This script performs the following steps:

  1. Query the VM Scale Set model and check the current OS version.
  2. Confirms OS upgrade with the user (unless --noprompt is used).
  3. Updates the VMSS model to the new version. At this point no VMs have been upgraded, unless the VMSS _upgradePolicy_ property is set to "Automatic").
  4. Does a _manualUpgrade_ on the VMs in the selected update domain (or specific VMs, depending on the command line parameters).
  5. Waits until the VMSS provisioning state has finished updating (unless the --nowait command line parameter is used).

![vmssupgrade screenshot](./docs/vmssupgrade-screenshot.png)

### Installation
  1. Install Python 3.x.
  2. Install the azurerm REST wrappers for Microsoft Azure: "pip install azurerm" (use --upgrade if azurerm is already installed)
  3. Clone this repo locally. In particular copy the vmssupgrade folder.
  4. You need a service principal and tenant ID. See [Authenticating a service principal with Azure Resource Manager](https://azure.microsoft.com/en-us/documentation/articles/resource-group-authenticate-service-principal/) - note that "Reader" access as described in that doc is not enough. It should be "Contributor" or some other roll that allows write access.
  6. Edit vmssconfig.json in the local directory (rename vmssconfig.json.tmpl). Fill in the service principal values for your application (tenantId, appId, app secret, subscription ID).
  7. usage: vmssupgrade -r rgname -s vmssname -n newversion {-u updatedomain|-i vmid|-l vmlist} [-y][-v][-h]
  
### Examples
  
**Upgrading a single VM in a VM Scale Set** 
  
This example upgrades VM id #1 and sets verbose mode, which will display the provisioning state every 5 seconds until complete..
  
vmssupgrade.py --resourcegroup myrg --vmssname myvmss --newversion "14.04.201506100" -i 1 -v

**Upgrading upgrade domain 0 of a VM Scale Set**

python vmssupgrade.py --resourcegroup myrg --vmssname myvmss --newversion "14.04.201507060" --updatedomain 0

**Upgrading a custom image URI in upgrade domain 0 of a VM Scale Set**

python vmssupgrade.py --resourcegroup myrg --vmssname myvmss --customuri "path_to_custom_image" --updatedomain 0

**Start an upgrade but don't wait for it to complete**

python vmssupgrade.py --resourcegroup myrg --vmssname myvmss --newversion "14.04.201507060" --updatedomain 0 --nowait

**Upgrade an arbitrary list of VMs in a VM Scale Set**

python vmssupgrade.py --resourcegroup myrg --vmssname myvmss --newversion "14.04.201507060" --vmlist '["1","2","3","4"]'

**Quick video walkthrough**

[![vmssupgrade demo](https://img.youtube.com/vi/0sc9YMgvXLY/0.jpg)](https://www.youtube.com/watch?v=0sc9YMgvXLY)

### Notes

- The ability to update an OS version in a running scale set was only recently enabled in production. Your account may need to be whitelisted if you try this before April 23 2016. Contact @gbowerman for more details.

- This script is light on error checking and should be thought of as a proof of concept. If you're thinking of using it in production you'd need to do some work on it to improve error handling and logging.

- This script is designed to work with both platform images (updates the _version_ property of the _imageReference_) and custom images (updating the _osDisk->image->Uri_), though custom image support hasn't been tested yet. Let me know if it works :-)

- You can update the version of a platform image. Updating the _sku_ (for example going from Ubuntu 15.10 to 16.04) is not possible. This maybe possible for VM Scale Sets in the future.
 