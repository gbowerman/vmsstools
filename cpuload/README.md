# Random load generator for Azure VM scale set VMs
A set of scripts to trigger a randmon CPU load against  the VMs in a scale set. Tested up to 1000 VMs.

To generate a load

1. Deploy a VM scale set which includes a custom script extension which deploys a Python bottle server: [https://github.com/gbowerman/azure-myriad/blob/master/bigtest/bigbottle.json](https://github.com/gbowerman/azure-myriad/blob/master/bigtest/bigbottle.json)
2. Deploy a jumpbox VM in the same subnet. E.g. use [https://github.com/gbowerman/vmsstools/tree/master/jumpbox](https://github.com/gbowerman/vmsstools/tree/master/jumpbox)
3. ssh to the jumpbox VM and use the getnics.py script to generate a list of VMSS VMs. Note: this requires an _azurermconfig.json_ file in the same directory which contains your service principal app/tenant details and subscription id.
   ```
   python3 getnics.py > ipaddrs
   ```
4. Edit random-load.py to set your resource group name and scale set name.
5. Start a load running in background with
   ```
   nohup python3 random-load.py > random.out 2>&1 &
   ```
6. Kill the process when you're done.
