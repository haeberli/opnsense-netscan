#!/usr/local/bin/python3

import sys 
import json
from utils import *

if len(sys.argv) != 2:
  print('MAC as argument required')
  exit()

hosts = gethosts()
h = next((i for i in hosts if i['MAC'] == sys.argv[1]), None) 
if not h:
  h = { 'MAC':sys.argv[1], 'Name':'', 'Device':''}

print(json.dumps(h)) 