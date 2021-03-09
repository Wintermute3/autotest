#!/bin/bash

# data collection loop

while true; do
  ./test.sh
  VARS='test-vars.sh'
  if [ -f "${VARS}" ]; then
    source test-vars.sh
    rm -f ${PREFIX}-u3-data.json ${PREFIX}-rd-pv.json ${PREFIX}-rd-bat.json
    echo -n "setting ${WAITFOR}"...
    touch ${WAITFOR}
    echo "running"
    ../at-u3.py -c=u3-config -o=${PREFIX}-u3-data
    rm -f ${WAITFOR}
    echo "done"
    echo
    ls -l *.json
  else
    echo "*** vars file '${VARS}' not found - run ./test.sh to configure!"
  fi
done
