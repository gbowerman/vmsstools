# Random load generator for Azure VM scale set VMs
A set of scripts to trigger a randmon CPU load against VMs in a scale set. This works by creating a standalone VM in the scale VNet as the scale set, and using this VM to query the internal IP addresses and send a load to them. Tested up to 1000 VMs.

To generate a load:

1. Deploy a VM scale set which includes a custom script extension which deploys a Python bottle server: [https://github.com/gbowerman/azure-myriad/blob/master/bigtest/bigbottle.json](https://github.com/gbowerman/azure-myriad/blob/master/bigtest/bigbottle.json)
2. Deploy a jumpbox VM in the same subnet. E.g. use [https://github.com/gbowerman/vmsstools/tree/master/jumpbox](https://github.com/gbowerman/vmsstools/tree/master/jumpbox)
3. ssh to the jumpbox VM and use the getnics.py script to generate a list of VMSS VM internal IP addresses. 

Note: This requires an _azurermconfig.json_ file in the same directory, which contains your service principal app/tenant details and subscription id. See azurermconfig.json.tmpl in this repo as an example.

Note: getnics.py currently has a hardcoded resource group and scale set name. You'll need to edit getnics.py to set your resource group and scale set.
   ```
   sudo apt install python3-pip
   sudo pip3 install azurerm
   curl https://raw.githubusercontent.com/gbowerman/vmsstools/master/cpuload/getnics.py > getnics.py
   curl https://raw.githubusercontent.com/gbowerman/vmsstools/master/cpuload/random-load.py > random-load.py
   vi getnics.py # put your RG and VMSS name here
   python3 getnics.py > ipaddrs
   ```
4. Start a load running in background with
   ```
   nohup python3 random-load.py > random.out 2>&1 &
   ```
5. Kill the process when you're done.
