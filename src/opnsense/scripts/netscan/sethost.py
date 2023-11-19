#!/usr/local/bin/python3

import sys 
import json
from utils import *

if len(sys.argv) != 2:
  print('Host as argument required')
  exit()

print(sys.argv[1])
h = json.loads(sys.argv[1])
h['Q'] = False

hosts = gethosts()
ho = next((i for i in hosts if i['MAC'] == h['MAC']), None) 
if ho:
  hosts.remove(ho)
hosts.append(h)
sethosts(hosts)