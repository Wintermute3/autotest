#!/bin/bash

# battery simulation, 20 seconds oscillating +/-1V around $VBAT

VARS='test-vars.sh'

if [ -f "${VARS}" ]; then
  while true; do
    unset R5 VBAT
    source test-vars.sh

#   ../at-rd6000.py -o=${R5}-${VBAT}-rd-bat.json -i=19103 -s=${START_FLAG} v=${VBAT},on,s=${DWELL},off,v=0

    ../at-rd6000.py -o=${R5}-${VBAT}-rd-bat.json -i=19103 -s=${START_FLAG} \
      v=${VBAT} \
      ocp=0.65 \
      on \
      [v+0.01,m=15]=150 \
      [v-0.01,m=15]=150 \
      v=0 \
      off

    rm -f ${START_FLAG}
    while [ ! -f ${END_FLAG} ]; do
      sleep 0.2
    done
  done
else
  echo "*** vars file '${VARS}' not found - run ./test.sh to configure!"
fi
