#!/bin/bash

# battery simulation, 23 seconds at 6.0v

VBAT=${1:-6.0}
HANG=23

../at-rd6000.py -o=rd-bat.json -i=19103 -s=rd-go v=${VBAT},on,s=${HANG},off,v=0
