# vmsstools
Azure VM Scale Set scripts

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
  3. Clone this repo locally.
  4. You need a service principal and tenant ID. See [Authenticating a service principal with Azure Resource Manager](https://azure.microsoft.com/en-us/documentation/articles/resource-group-authenticate-service-principal/).
  6. Edit vmssconfig.json in the local directory (rename vmssconfig.json.tmpl). Fill in the service principal values for your application (tenantId, appId, app secret, subscription ID).
  7. usage: vmssupgrade -r rgname -s vmssname -n newversion {-u updatedomain|-i vmid|-l vmlist} [-y][-v][-h]
  
### Examples
  
**Upgrading a single VM in a VM Scale Set** 
  
This example upgrades VM id #1 and sets verbose mode, which will display the provisioning state every 5 seconds until complete..
  
vmssupgrade.py --resourcegroup myrg --vmssname myvmss --newversion "14.04.201506100" -i 1 -v

**Upgrading upgrade domain 0 of a VM Scale Set**

python vmssupgrade.py --resourcegroup myrg --vmssname myvmss --newversion "14.04.201507060" --updatedomain 0

**Start an upgrade but don't wait for it to complete**

python vmssupgrade.py --resourcegroup myrg --vmssname myvmss --newversion "14.04.201507060" --updatedomain 0 --nowait

**Upgrade an arbitrary list of VMs in a VM Scale Set**

python vmssupgrade.py --resourcegroup myrg --vmssname myvmss --newversion "14.04.201507060" --vmlist '["1","2","3","4"]'

### Notes

- This version only works with platform images (updates the _version_ property of the _imageReference_). Support for custom images will be added in a future version (updating the _imageUri_).

- You can only update the version of a platform image. Updating the _sku_ (for example going from Ubuntu 15.10 to 16.04) is not possible. This maybe possible for VM Scale Sets in the future.
 