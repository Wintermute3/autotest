#!/bin/bash

# set test title and filename suffix

VARS='test-vars.sh'
WAITFOR=test.go

echo
echo 'test set configuration'
echo

if [ -f "${VARS}" ]; then
  source ${VARS}
  echo '  current configuration:'
  echo
  echo "    title for graphs: ${TITLE}"
  echo "    title for graphs: ${WAITFOR}"
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
echo '#!/bin/bash'                 >  "${VARS}"
echo                               >> "${VARS}"
echo "export TITLE='${TITLE}'"     >> "${VARS}"
echo "export R5='${R5}'"           >> "${VARS}"
echo "export VBAT='${VBAT}'"       >> "${VARS}"
echo "export WAITFOR='${WAITFOR}'" >> "${VARS}"
echo                               >> "${VARS}"
echo "configuration file '${VARS} updated"
echo
