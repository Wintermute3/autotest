#!/usr/bin/env python3

#==============================================================================
# graph a json dataset
#==============================================================================

PROGRAM = 'at-graph.py'
VERSION = '2.102.181'
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

DataSetFileName = 'at-dataset.json'
MappingFileName = 'at-mapping.json'

def ShowHelp():
  HelpText = '''\
    graph a json dataset

usage:

    %s [-h] [-f=filename[.json]]

where:

    -h . . . . . . this help text
    -d=xxxx  . . . name of dataset file (default '%s')
    -m=xxxx  . . . name of mapping file (default '%s')
'''
  print(HelpText % (sys.argv[0], DataSetFileName, MappingFileName))
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
    elif arg.startswith('-d='):
      try:
        DataSetFileName = arg[3:]
        if len(DataSetFileName) < 1:
          ShowErrorToken(arg)
        if not '.' in DataSetFileName:
          DataSetFileName += '.json'
      except:
        ShowErrorToken(arg)
    elif arg.startswith('-m='):
      try:
        MappingFileName = arg[3:]
        if len(MappingFileName) < 1:
          ShowErrorToken(arg)
        if not '.' in MappingFileName:
          MappingFileName += '.json'
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
  DataSet = json.load(open(DataSetFileName))
  try:
    Mapping = json.load(open(MappingFileName))
    for Channel in Mapping['channels']:
      if not Channel['name'] in DataSet['channels']:
        print("*** mapping channel '%s' not found in dataset!" % (Channel['name']))
        os._exit(1)
    try:
      X = []
      for Item in DataSet['data']:
        X.append(Item['time'])
      print('  graphing %d values' % (len(X)))
      plt.xlabel(Mapping['x-axis']['label'])
      for MappingChannel in Mapping['channels']:
        for Index, DataChannel in enumerate(DataSet['channels']):
          if DataChannel == MappingChannel['name']:
            Tare   = MappingChannel['tare'  ]
            Scale  = MappingChannel['scale' ]
            Offset = MappingChannel['offset']
            Y = []
            for Item in DataSet['data']:
              Value = float(Item['values'][Index])
              Y.append(((Value - Tare) * Scale) + Offset)
            plt.plot(X, Y)
            plt.ylabel(DataSet['channels'][Index])
      print()
      print('  dataset: %s' % (DataSetFileName))
      print('  mapping: %s' % (MappingFileName))
      plt.show()
    except:
      print("*** error rendering plot!")
  except:
    print("*** unable to open mapping file '%s' for input!" % (MappingFileName))
except:
  print("*** unable to open dataset file '%s' for input!" % (DataSetFileName))
print()

#==============================================================================
# end
#==============================================================================
