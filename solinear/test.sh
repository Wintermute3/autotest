#!/bin/bash

# set test title and filename suffix

VARS='test-vars.sh'
WAITFOR=test.go

echo
echo 'test set configuration'
echo
echo -n '  title for graphs: '; read TITLE
echo -n '  prefix for files: '; read PREFIX
echo
echo '#!/bin/bash'                 >  "${VARS}"
echo                               >> "${VARS}"
echo "export TITLE='${TITLE}'"     >> "${VARS}"
echo "export PREFIX='${PREFIX}'"   >> "${VARS}"
echo "export WAITFOR='${WAITFOR}'" >> "${VARS}"
echo                               >> "${VARS}"
echo "vars file '${VARS} updated"
echo
