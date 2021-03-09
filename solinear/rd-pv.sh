#!/bin/bash

# pv simulation, 8s ramp to 10v, 5s hold, 8s ramp to 0v

VARS='test-vars.sh'
if [ -f "${VARS}" ]; then
  while true; do
    source test-vars.sh
    ../at-rd6000.py -o=${PREFIX}-rd-pv.json -i=18927 -s=${WAITFOR} v=0,on [v+0.5,s=0.2]=20 s=5 [v-0.5,s=0.2]=20 off
  done
else
  echo "*** vars file '${VARS}' not found - run ./test.sh to configure!"
fi
