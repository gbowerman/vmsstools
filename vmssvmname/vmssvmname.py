# vmssvmname.py - convert a VMSS VM hostname into a VM id and vice versa
# VM references can look like:
#     instanceId = 1146
#     name = myvmss_1146
#     hostname = vmssprefix0000VU
#     roleinstancename = aks-agentpool-33143703-vmss_128 or _aks-agentpool-33143703-vmss_128
import argparse
import sys
import re


def hostname_to_vmid(hostname):
    # get last 6 characters and remove leading zeroes
    hexatrig = hostname[-6:].lstrip('0').upper()
    multiplier = 1
    vmid = 0
    # reverse string and process each char
    for x in hexatrig[::-1]:
        if x.isdigit():
            vmid += int(x) * multiplier
        else:
            # convert letter to corresponding integer
            vmid += (ord(x) - 55) * multiplier
        multiplier *= 36
    return vmid


def vmid_to_hostname(vmid, prefix):
    hexatrig = ''
    # convert decimal vmid to hexatrigesimal base36
    while vmid > 0:
        vmid_mod = vmid % 36
        # convert int to corresponding letter
        if vmid_mod > 9:
            char = chr(vmid_mod + 55)
        else:
            char = str(vmid_mod)
        hexatrig = char + hexatrig
        vmid = int(vmid/36) 
    return (prefix + hexatrig.zfill(6)).lower()


# validate command line arguments
argParser = argparse.ArgumentParser()

argParser.add_argument('--hostname', '-n', required=False,
                       action='store', help='VMSS VM hostname')
argParser.add_argument('--prefix', '-p', required=False,
                       action='store', help='VMSS machine name prefix')
argParser.add_argument('--vmid', '-i', type=int, required=False,
                       action='store', help='VM ID')
argParser.add_argument('--roleinstancename', '-r', required=False,
                       action='store', help='Role instance name')
args = argParser.parse_args()

hostname = args.hostname
vmid = args.vmid
prefix = args.prefix
roleinstancename = args.roleinstancename

if roleinstancename is not None:
    m = re.search('(aks.*vmss)_(\d+)',roleinstancename)
    hostname = vmid_to_hostname(int(m[2]),m[1])
    print('hostname = ' + hostname)
elif hostname is None:
    if vmid is None or prefix is None:
        sys.exit('Error: Provide a value for --hostname, or --vmid and --prefix, or --roleinstancename.')
    hostname = vmid_to_hostname(vmid, prefix)
    print('hostname = ' + hostname.lower())
else:
    if vmid is not None:
        sys.exit('Error: Provide a value for --hostname, or --vmid and --prefix, or --roleinstancename')
    vmid = hostname_to_vmid(hostname)
    print('VM ID = ' + str(vmid))