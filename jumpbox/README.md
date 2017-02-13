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

![jumpbox screenshot](../docs/jumpbox.png)

### Installation
  1. Install Python 3.x.
  2. Install the azurerm REST wrappers for Microsoft Azure: "pip install azurerm" (use --upgrade if azurerm is already installed).
  3. Clone this repo locally. 
  4. You need a service principal and tenant ID. See [Authenticating a service principal with Azure Resource Manager](https://azure.microsoft.com/en-us/documentation/articles/resource-group-authenticate-service-principal/) - note that "Reader" access as described in that doc is not enough. It should be "Contributor" or some other roll that allows write access.
  6. Edit azurermconfig.json in the local directory (rename azurermconfig.json.tmpl). Fill in the service principal values for your application (tenantId, appId, app secret, subscription ID).