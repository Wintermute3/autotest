#!/bin/bash

# graph the results of a test

VARS='test-vars.sh'

if [ -f "${VARS}" ]; then
  source test-vars.sh
  ../at-graph.py $@ -d=${PREFIX}-u3-data -m=graph -p=${PREFIX} -t="$TITLE"
else
  echo "*** vars file '${VARS}' not found - run ./test.sh to configure!"
fi
