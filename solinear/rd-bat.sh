#!/bin/bash

# battery simulation, 22 seconds at $VBAT

VARS='test-vars.sh'
DWELL=22

if [ -f "${VARS}" ]; then
  while true; do
    unset R5 VBAT
    source test-vars.sh
    ../at-rd6000.py -o=${R5}-${VBAT}-rd-bat.json -i=19103 -s=${START_FLAG} v=${VBAT},on,s=${DWELL},off,v=0
    rm -f ${START_FLAG}
    while [ ! -f ${END_FLAG} ]; do
      sleep 0.2
    done
  done
else
  echo "*** vars file '${VARS}' not found - run ./test.sh to configure!"
fi
