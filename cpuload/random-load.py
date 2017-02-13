from random import randint
import requests
import sys
import time

PORT = 9000

def ipaddr_on(ipaddr):
    url = 'http://' + ipaddr + ':' + str(PORT) + '/do_work'
    requests.get(url)

def ipaddr_off(ipaddr):
    url = 'http://' + ipaddr + ':' + str(PORT) + '/stop_work'
    requests.get(url)

# load ip addresses
try:
   addrlist = open('ipaddrs').read().splitlines()
except FileNotFoundError:
   print("Error: Expecting file ipaddrs in current folder")
   sys.exit()

total_machines = len(addrlist)

# main loop
while True:
    # pick a random time
    loop_time = randint(180, 1200) # random time between 3 and 20 mins
    print('Run for ' + str(loop_time) + ' seconds')
  
    # pick a random number of machines between 20 and 100% of total
    machine_count = randint(total_machines//5, total_machines)
    print('Hit ' + str(machine_count) + ' machines')

    # activate that many machines
    for i in range(machine_count):
        ipaddr_on(addrlist[i])
    time.sleep(loop_time)
    # after time internval switch them off 
    for j in range(machine_count):
        ipaddr_off(addrlist[j])
 