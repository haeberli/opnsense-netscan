#!/bin/sh

OUTFILE="/tmp/netscan.txt"

: > $OUTFILE

echo "*** Start net scan ***" >> $OUTFILE
arp-scan -I bridge0 -l >> $OUTFILE

echo '* Updating *' >> $OUTFILE
/usr/local/bin/python3 /usr/local/opnsense/scripts/netscan/update.py >> $OUTFILE

echo "*** End net scan ***" >> $OUTFILE
