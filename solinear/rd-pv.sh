#!/bin/bash

# pv simulation, set to 10v, 10s hold, set to 0v

VARS='test-vars.sh'
if [ -f "${VARS}" ]; then
  while true; do
    unset R5 VBAT
    source test-vars.sh

#   ../at-rd6000.py -o=${R5}-${VBAT}-rd-pv.json -i=18927 -s=${START_FLAG} v=0,on [v+0.5,s=0.2]=20 s=5 [v-0.5,s=0.2]=20 off

    ../at-rd6000.py -o=${R5}-${VBAT}-rd-pv.json -i=18927 -s=${START_FLAG} \
    v=0 \
    ocp=0.35 \
    on \
    s=1 \
    v=10 \
    s=38 \
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
