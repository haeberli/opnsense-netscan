#!/usr/local/bin/python3
#/usr/local/bin/python3 /usr/local/opnsense/scripts/netscan/update.py

from utils import *
import subprocess
import ujson
import re
from datetime import datetime
import os

FILE='/tmp/netscan.json'

PA_PREFIX='192.168.74.'
GUA_PREFIX='2a04:ee41:81:6063:'
DOMAIN_POSTFIX='.tigerduck.com.'

print('### START UPDATE ###')

# get hosts
host = gethosts()

print('Host has', len(host), 'entries')
for hoste in host:
  print('-', hoste['MAC'], hoste['Q'], hoste['Name'], hoste['Device'])

# get current arp
arp_raw = subprocess.run(['arp', '-an'], capture_output=True, text=True).stdout.splitlines()

arp_re = re.compile(r'^\S+ \((?P<IPV4>[^\)]+)\) at (?P<MAC>(?:[0-9a-f]{2}:){5}(?:[0-9a-f]{2})) on .*$')
arp = [arp_re.match(i).groupdict() for i in arp_raw if arp_re.match(i)]
arp.sort(key=lambda e: e['MAC'])

print('ARP has', len(arp), 'entries')
for arpe in arp:
  print('-', arpe['MAC'], arpe['IPV4'])

# get current ndp
ndp_raw = subprocess.run(['ndp', '-an'], capture_output=True, text=True).stdout.splitlines()  

ndp_re = re.compile(r'^(?P<IPV6>(?:[0-9a-f:]+)).*(?P<MAC>(?:[0-9a-f]{2}:){5}(?:[0-9a-f]{2})).*$')
ndp = [ndp_re.match(i).groupdict() for i in ndp_raw if ndp_re.match(i)]
ndp.sort(key=lambda e: e['MAC'])

print('NDP has', len(ndp), 'entries')
for ndpe in ndp:
  print('-', ndpe['MAC'], ndpe['IPV6'])

# get oui
oui = {}
oui_re = re.compile(r'^(?P<OUI>(?:[0-9A-F]{6}))\s+(?P<Vendor>.*)$')
with open('/usr/local/share/arp-scan/ieee-oui.txt') as oui_raw:
  for oui_line in oui_raw:
    m = oui_re.match(oui_line)
    if m:
      oui[m['OUI']] = m['Vendor']

print('OUI has', len(oui), 'entries')

# build result from last and mac
result = []
if os.path.isfile(FILE):
  with open(FILE) as file:
    result = ujson.load(file)

mac  = set([i['MAC'] for i in result]
         + [i['MAC'] for i in host]
         + [i['MAC'] for i in arp]
         + [i['MAC'] for i in ndp])

print('Scan', len(mac), 'entries,', len(result), 'entries from last')

# build result
store = False

for m in mac:
  print('-', m)
  now = datetime.now().isoformat(timespec='seconds')

  # ensure record
  r = next((i for i in result if i['MAC'] == m), None)
  if not r:
    r = {'MAC':m, 'Last':None,
         'IPV4a':[], 'IPV4':'', 'IPV6a':[], 'IPV6':'',
         'N4a':[], 'N6a':[], 'NMa':[], 'NTa':[],
         'Type':'', 'N':'', 'Name':'', 'Device': ''}
    result.append(r)

  # ip4
  ipv4 = [i['IPV4'] for i in arp if i['MAC'] == m]
  if ipv4:
    r['Last'] = now
    r['IPV4a'] = ipv4
    r['IPV4'] = '\\'.join(sorted([i.replace(PA_PREFIX,'PA: ') for i in ipv4]))

  # ip6
  ipv6 = [i['IPV6'] for i in ndp if i['MAC'] == m]
  if ipv6:
    r['Last'] = now
    r['IPV6a'] = ipv6
    r['IPV6'] = '\\'.join(sorted([i.replace('fe80::','LLA: ').replace(GUA_PREFIX,'GUA: ') for i in ipv6]))
    
  # dns entries
  r['N4a'] = [j.replace(DOMAIN_POSTFIX, '') for i in r['IPV4a'] for j in getdnsname(i)]
  r['N6a'] = [j.replace(DOMAIN_POSTFIX, '') for i in r['IPV6a'] for j in getdnsname(i)]

  # mdns entries
  if ipv4 and not r['NMa']:
    ret = [j for i in ipv4 for j in getmdnsname(i)]
    nma = [i.replace('.local.', '') for i in ret[0]]
    nta = [i for i in ret[1]]
    if nma:
      r['NMa'] = nma
    if nta:
      r['NTa'] = nta

  print('  Last seen:', ('now' if r['Last'] == now else r['Last']))
  print('  IPv4:', r['IPV4'], '\\'.join(r['N4a']), '\\'.join(r['NMa']))
  print('  IPv6:', r['IPV6'], '\\'.join(r['N6a']))
  if r['NTa']:
    print('  TXT:', '\\'.join(r['NTa']))
         
  # name, device
  name = None
  device = None
 
  h = next((i for i in host if i['MAC'] == m and not i['Q']), None)
  if h:
    # from hosts
    name = h['Name']
    device = h['Device']
  else:
    if r['Type']:
      name = r['N']
      device = r['Device']

    # shelly
    if ipv4 and [i for i in r['NMa'] if i.startswith('shelly')]:
      if r['Type'] != 'SHELLY':
        shelly = next((getshellysettings(i) for i in ipv4), None)
        if shelly:
          name = shelly['name']
          device = 'Shelly ' + shelly['device']['type']
          r['Type'] = 'SHELLY'
          print('  -> SHELLY', name, device)

    # bose
    if ipv4 and [i for i in r['NMa'] if i.startswith('Bose-SM2')]:
      if r['Type'] != 'BOSE':
        bose = next((getboseinfo(i) for i in ipv4), None)
        if bose:
          name = bose['info']['name']
          device = 'Bose ' + bose['info']['type']
          r['Type'] = 'BOSE'
          print('  -> BOSE', name, device)

    # wiz
    if ipv4 and m.startswith('44:4f:8e:'):
      if r['Type'] != 'WIZ':
        wiz = next((getwizsystemconfig(i) for i in ipv4), None)
        if wiz:
          device = 'WiZ ' + wiz['result']['moduleName']
          r['Type'] = 'WIZ'
          print('  -> WIZ', device)

    # fallback
    h = next((i for i in host if i['MAC'] == m and i['Q']), None)
    if not name:
      names = sorted(r['N4a']) + sorted(r['N6a']) + sorted(r['NMa'])
      name = names[0] if names else h['Name'] if h else '???'
    if not device:
      dt = '\\'.join([i.replace('\"model=J105aAP\"', 'Apple TV 4K').replace('\"model=J517AP\"', 'Apple iPad Pro 11 (3th Gen)') for i in r['NTa']])
      device = h['Device'] if h else dt if dt else oui.get(m.replace(':', '')[:6].upper(),  '???')

    # update hosts
    if h:
      if h['Name'] != name:
        h['Name'] = name
        store = True
        print('  -> Update host name to', name)
      if h['Device'] != device:
        h['Device'] = device
        store = True
        print('  -> Update device to', device)
    else:
      host.append({"MAC":m, "Q":True, "Name":name, "Device":device})
      store = True
      print('  -> Add host', name, device)
  
  r['N'] = name
  r['Name'] = (name +
              ''.join([' (A)' for i in r['N4a'] if i == name]) +
              ''.join([' (AAAA)' for i in r['N6a'] if i == name]) +
              ''.join([' (M)' for i in r['NMa'] if i == name]) +
              ''.join(['\\~A: ' + i for i in r['N4a'] if i != name]) +
              ''.join(['\\~AAAA: ' + i for i in r['N6a'] if i != name]) +
              ''.join(['\\~M:' + i for i in r['NMa'] if i != name]))
  r['Device'] = device

  print('  Name:', r['Name'])
  print('  Device:', r['Device'])
  print('  Type:', r['Type'])

# write hosts
if store:
  print('Storing', len(host), 'host entries')
  sethosts(host)

# write
result.sort(key=lambda e: tuple(int(j) for i in e['IPV4a'] for j in i.split('.')) + tuple(int(i, base=16) for i in e['MAC'].split(':')))
json = ujson.dumps(result, indent=2)

print('Storing', len(result), 'entries')

with open(FILE, 'w') as file:
  file.write(json)

print('### END UPDATE ###')
