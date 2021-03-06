#!/bin/bash

# battery simulation

VBAT=${1:-6.0}
HANG=23

WAITFOR=.go

echo -n "waiting for ${WAITFOR}"...
while [ ! -f ${WAITFOR} ]; do
	sleep 0.2
done
echo "running for ${HANG} seconds at ${VBAT} volts"

../at-rd6000.py -o=rd-bat.json -i=2 v=${VBAT},on,s=${HANG},off,v=0

echo "done"
