#!/bin/bash

# data collection loop

while true; do
  ./test.sh
  VARS='test-vars.sh'
  if [ -f "${VARS}" ]; then
    unset R5 VBAT
    source test-vars.sh
    rm -f ${R5}-${VBAT}-u3-data.json ${R5}-${VBAT}-rd-pv.json ${R5}-${VBAT}-rd-bat.json
    echo -n "setting ${WAITFOR}"...
    echo "running"
    ../at-u3.py -c=u3-config -o=${R5}-${VBAT}-u3-data -s=${WAITFOR}
    rm -f ${WAITFOR}
    echo "done"
    echo
    ls -l *.json
  else
    echo "*** vars file '${VARS}' not found - run ./test.sh to configure!"
  fi
done
