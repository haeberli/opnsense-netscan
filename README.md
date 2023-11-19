# os-netscan
Net Scan repo by haeberli

## Prepare environment on OPNsense host
Run on command line to install development tools
```
opnsense-code tools plugins
```
Setup Github connection
* Create .ssh folder (if required)
* Copy private key to /root/.ssh/id_ed25519
* Copy public key to /root/.ssh/id_ed25519.pub

Adjust permissions
```
chmod 700 /root/.ssh
chmod 600 /root/.ssh/id_ed25519
```
Check Github connection
```
ssh -vT git@github.com
```
Inital get
```
cd /usr/plugins/devel/
git clone git@github.com:haeberli/opnsense-netscan.git netscan
cd netscan
```
Install arp-scan
* Enable FreeBSD repo: /usr/local/etc/pkg/repos/FreeBSD.conf: set enabled to yes
* SSH: pkg install arp-scan
* Disable FreeBSD repo: Switch back to no
* Test: arp-scan -I bridge0 -l

## Create and install package
```
make upgrade
```
Create cron job
* Minutes: 0,5,0,15,20,25,30,35,40,45,50,55
* Hours: *
* Command: Scan net
* Description: Scan net
