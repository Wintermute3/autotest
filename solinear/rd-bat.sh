#!/bin/bash

# battery simulation, 23 seconds at 6.0v

VARS='test-vars.sh'
if [ -f "${VARS}" ]; then
  source test-vars.sh
  VBAT=${1:-6.0}
  HANG=23
  ../at-rd6000.py -o=${PREFIX}-rd-bat.json -i=19103 -s=${WAITFOR} v=${VBAT},on,s=${HANG},off,v=0
else
  echo "*** vars file '${VARS}' not found - run ./test.sh to configure!"
fi
