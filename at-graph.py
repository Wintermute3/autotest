#!/usr/bin/env python3

#==============================================================================
# graph a json dataset
#==============================================================================

PROGRAM = 'at-graph.py'
VERSION = '2.102.171'
CONTACT = 'bright.tiger@mail.com' # michael nagy

import os, sys, time, json
import datetime as dt

print()
print("%s %s" % (PROGRAM, VERSION))
print()

#==============================================================================
# import non-default libraries
#==============================================================================

def ImportError(Library):
  print('%s' % ( '''\
*** the python3 library '%s' is not installed.  to fix this
*** sad state of affairs, run the following command and try again:

  pip3 install %s
''') % (Library, Library))
  os._exit(1)

try:
  import numpy
except:
  ImportError('numpy')

try:
  import matplotlib.pyplot as plt
  import matplotlib.dates as md
except:
  ImportError('matplotlib')

#==============================================================================
# show usage help
#==============================================================================

FileName = '.%s.json' % (PROGRAM.split('.')[0])

def ShowHelp():
  HelpText = '''\
    graph a json dataset

usage:

    %s [-h] [-f=filename[.json]]

where:

    -h . . . . . . this help text
    -i=# . . . . . specify multimeter index (default 1)
    -f=xxxx  . . . name of output file (default '%s')
'''
  print(HelpText % (sys.argv[0], FileName))
  os._exit(1)

#==============================================================================
# parse error
#==============================================================================

def ShowError(Message=None):
  print('*** the command line:')
  print()
  print('  %s' % (' '.join(sys.argv)))
  print()
  if Message:
    print('*** %s' % (Message))
  else:
    print('*** could not be parsed. see the -h help information!')
  print('*** see the -h help information!')
  print()
  os._exit(1)

def ShowErrorToken(Token):
  ShowError('could not be parsed because of this token: %s' % (Token))

#==============================================================================
# parse arguments
#==============================================================================

for arg in sys.argv[1:]:
  if arg.startswith('-'):
    if arg == '-h':
      ShowHelp()
    elif arg.startswith('-f='):
      try:
        FileName = arg[3:]
        if len(FileName) < 1:
          ShowErrorToken(arg)
        if not '.' in FileName:
          FileName += '.json'
      except:
        ShowErrorToken(arg)
    else:
      ShowErrorToken(arg)
  else:
    ShowErrorToken(arg)

#==============================================================================
# graph a dataset
#==============================================================================

try:
  DataSet = json.load(open(FileName))
  X = []
  Y = []
  for Item in DataSet['data']:
    X.append(Item['time'])
    Y.append(Item['values'][0])
  print('  graphing %d values' % (len(X)))
  plt.plot(X, Y)
  plt.xlabel('time')
  plt.ylabel(DataSet['channels'][0])
  plt.show()
except:
  print("*** unable to open file '%s' for input!" % (FileName))
print()

#==============================================================================
# end
#==============================================================================
