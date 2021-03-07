#!/bin/bash

# data collection

VARS='test-vars.sh'
if [ -f "${VARS}" ]; then
  source test-vars.sh
  rm -f u3-output.json rd-pv.json rd-bat.json
  echo -n "setting ${WAITFOR}"...
  touch ${WAITFOR}
  echo "running"
  ../at-u3.py -c=u3-config -o=${PREFIX}
  rm -f ${WAITFOR}
  echo "done"
  echo
  ls -l *.json
else
  echo "*** vars file '${VARS}' not found - run ./test.sh to configure!"
fi
