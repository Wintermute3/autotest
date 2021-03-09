#!/bin/bash

# set test title and filename suffix

VARS='test-vars.sh'
TITLE='solinear'
START_FLAG='at-u3.go'
END_FLAG='at-u3.end'

echo
echo 'test set configuration'
echo

if [ -f "${VARS}" ]; then
  unset TITLE START_FLAG R5 VBAT
  source ${VARS}
  echo '  current configuration:'
  echo
  echo "    title for graphs: ${TITLE}"
  echo "          start flag: ${START_FLAG}"
  echo "            end flag: ${END_FLAG}"
  echo
  echo "       r5 resistance: ${R5}"
  echo "     battery voltage: ${VBAT}"
fi
echo
echo '  new configuration (^c to cancel changes):'
echo
echo -n '      r5 resistance: '; read R5
echo -n '    battery voltage: '; read VBAT
echo
echo '#!/bin/bash'                       >  "${VARS}"
echo                                     >> "${VARS}"
echo "export TITLE='${TITLE}'"           >> "${VARS}"
echo "export START_FLAG='${START_FLAG}'" >> "${VARS}"
echo "export END_FLAG='${END_FLAG}'"     >> "${VARS}"
echo                                     >> "${VARS}"
echo "export R5='${R5}'"                 >> "${VARS}"
echo "export VBAT='${VBAT}'"             >> "${VARS}"
echo                                     >> "${VARS}"
echo "configuration file '${VARS} updated"
echo
