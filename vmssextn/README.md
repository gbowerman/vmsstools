## vmssextn

Tool to read, add, remove extensions from an Azure VM Scale Set.

![vmssextn screenshot](../docs/vmssextn_show.png)

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



### Installation

  1. Install Python 3.x.
  2. Install the azurerm REST wrappers for Microsoft Azure: "pip install azurerm" (use --upgrade if azurerm is already installed)
  3. Clone this repo locally. In particular copy the vmssextn folder.
  4. You need a service principal and tenant ID. See [Authenticating a service principal with Azure Resource Manager](https://azure.microsoft.com/en-us/documentation/articles/resource-group-authenticate-service-principal/) - note that "Reader" access as described in that doc is not enough. It should be "Contributor" or some other roll that allows write access.
  6. Edit vmssconfig.json in the local directory (rename vmssconfig.json.tmpl). Fill in the service principal values for your application (tenantId, appId, app secret, subscription ID).
  7. Run the command, e.g. python vmssextn.py