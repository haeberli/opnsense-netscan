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
## Create and install package
```
make upgrade
```
