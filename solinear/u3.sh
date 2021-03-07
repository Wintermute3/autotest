#!/bin/bash

# data collection

WAITFOR=rd-go

rm -f u3-output.json rd-pv.json rd-bat.json

echo -n "setting ${WAITFOR}"...
touch ${WAITFOR}
echo "running"

../at-u3.py -c=u3-config

rm -f ${WAITFOR}
echo "done"
echo
ls -l *.json