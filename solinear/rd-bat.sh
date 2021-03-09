#!/bin/bash

# battery simulation, 23 seconds at 6.0v

VARS='test-vars.sh'
if [ -f "${VARS}" ]; then
  HANG=23
  while true; do
    unset R5 VBAT
    source test-vars.sh
    ../at-rd6000.py -o=${R5}-${VBAT}-rd-bat.json -i=19103 -s=${WAITFOR} v=${VBAT},on,s=${HANG},off,v=0
    rm -f ${WAITFOR}
  done
else
  echo "*** vars file '${VARS}' not found - run ./test.sh to configure!"
fi
