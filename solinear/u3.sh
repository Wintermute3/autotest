#!/bin/bash

# data collection loop

VARS='test-vars.sh'

while true; do
  ./test.sh
  rm -f ${START_FLAG} ${END_FLAG}
  if [ -f "${VARS}" ]; then
    unset R5 VBAT
    source test-vars.sh
    rm -f "${R5}-${VBAT}-u3-data.json" \
          "${R5}-${VBAT}-rd-pv.json"   \
          "${R5}-${VBAT}-rd-bat.json"
    ../at-u3.py -c=u3-config -o="${R5}-${VBAT}-u3-data" -s="${START_FLAG}"
    rm -f ${START_FLAG}
    touch ${END_FLAG}
    echo "done"
    echo
    ls -l ${R5}-${VBAT}-*.json
  else
    echo "*** vars file '${VARS}' not found - run ./test.sh to configure!"
  fi
done
