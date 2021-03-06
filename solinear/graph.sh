#!/bin/bash

# graph the results of a test

VARS='test-vars.sh'

if [ -f "${VARS}" ]; then
  unset R5 VBAT TITLE
  source test-vars.sh
  ../at-graph.py $@ -d="${R5}-${VBAT}-u3-data" -m=graph -p="${R5}-${VBAT}" -t="${TITLE}-${R5}-${VBAT}"
else
  echo "*** vars file '${VARS}' not found - run ./test.sh to configure!"
fi
