#!/usr/local/bin/python3
#cd /usr/local/opnsense/scripts/netscan/
#/usr/local/bin/python3 -c 'from utils import *; print(getshellysettings("192.168.74.100"))' 

import subprocess
import re
import os
import requests
import xmltodict
import json

HOST_FILE='/var/netscan.txt'

DIGARGS = ['+noauthority', '+noclass', '+nocmd', '+nocomments', '+nocookie', '+nocrypto', '+noquestion' ,'+norrcomments', '+nostats', '+nottlid', '+time=1', '+tries=3']
dig_re = re.compile(r'PTR\s+(?P<DOMAIN>.*)\n')
digtxt_re = re.compile(r'TXT\s+(?P<DOMAIN>.*)\n')
    
def getdnsname(ip):
  dig_raw = subprocess.run(['dig', '-x', ip] + 
    DIGARGS, capture_output=True, text=True).stdout
  ret = dig_re.findall(dig_raw)
  ret.sort()
 
  print('  -> DNS', ip, ret)
  return ret
 
def getmdnsname(ip):
  dig_raw = subprocess.run(['dig', '-x', ip, '-p', '5353', '@' + ip] + 
    DIGARGS, capture_output=True, text=True).stdout
  ret = dig_re.findall(dig_raw)
  rettxt = digtxt_re.findall(dig_raw)
  if not ret:
    dig_raw = subprocess.run(['dig', '-x', ip, '-p', '5353', '@224.0.0.251'] + 
      DIGARGS, capture_output=True, text=True).stdout
    ret = dig_re.findall(dig_raw)
    rettxt = digtxt_re.findall(dig_raw)
 
  print('  -> mDNS', ip, ret, rettxt)
  return ret, rettxt

def gethosts():
  hosts = []
  if os.path.isfile(HOST_FILE):
    host_re = re.compile(r'^(?P<MAC>\S+)\s+(?P<Q>\??)(?P<Name>\S+)\s+(?P<Device>.*)$')
    with open(HOST_FILE) as host_raw:
      for host_line in host_raw:
        m = host_re.match(host_line)
        if m:
          hosts.append({"MAC": m['MAC'], "Q": m['Q'] == '?', "Name": m['Name'], "Device": m['Device'] })
  hosts.sort(key=lambda e: ('~' if e['Q'] else '') + e['MAC'])
  return hosts

def sethosts(hosts):
  with open(HOST_FILE, 'w') as host_raw:
    hosts.sort(key=lambda e: ('~' if e['Q'] else '') + e['MAC'])
    for h in hosts:
      print(h['MAC'], ('?' if h['Q'] else '') + h['Name'], h['Device'], file=host_raw)

def getshellysettings(ip):
  try:
    r = requests.get('http://' + ip + '/settings', timeout=30)
    print('  -> Shelly Settings', r.status_code)
    return r.json()
  except Exception:
    print('  -> Shelly Settings failed')
    return None 

def getboseinfo(ip):
  try:
    r = requests.get('http://' + ip + ':8090/info', timeout=10)
    print('  -> Bose Info', r.status_code)
    return xmltodict.parse(r.text)
  except Exception:
    print('  -> Bose Info failed')
    return None

def getwizsystemconfig(ip):
  try:
    r = subprocess.run(['nc', '-u', '-w', '1', ip, '38899'],
      input='{"method":"getSystemConfig","params":{}}', encoding='ascii',
      capture_output=True, text=True).stdout
    print('  -> WiZ SystemConfig', r)
    return json.loads(r)
  except Exception:
    print('  -> WiZ SystemConfig failed')
    return None