#!/usr/bin/env python3

#==============================================================================
# graph a json dataset
#==============================================================================

PROGRAM = 'at-graph.py'
VERSION = '2.102.271'
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
  import numpy as np
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

    %s [-h] [-d=filename[.json]] [-m=filename[.json]] [-c#[#]]

where:

    -h . . . . . . this help text
    -d=xxxx  . . . name of dataset file (default '%s')
    -m=xxxx  . . . name of mapping file (default '%s')
    -c=##  . . . . channel selector(s) (optional)

channel selectors, if specified, are a list of digits which identify the
indexes of the data channels to graph.  for instance:

    -c42

selects channels 4 and 2, in that order, with the first becoming the left
axis and the second becoming the right axis.
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
      fig, axis1 = plt.subplots()
      if 'title' in Mapping:
        plt.title(Mapping['title'])
      if 'x-axis' in Mapping and 'label' in Mapping['x-axis']:
        axis1.set_xlabel(Mapping['x-axis']['label'])
      axis2 = None
      Lines = []
      Labels = []
      for ChannelIndex, MappingChannel in enumerate(Mapping['channels']):
        for Index, DataChannel in enumerate(DataSet['channels']):
          if DataChannel == MappingChannel['name']:
            Tare = 0.0
            Scale = 1.0
            Offset = 0.0
            if 'tare' in MappingChannel:
              Tare   = MappingChannel['tare'  ]
            if 'scale' in MappingChannel:
              Scale  = MappingChannel['scale' ]
            if 'offset' in MappingChannel:
              Offset = MappingChannel['offset']
            Y = []
            for Item in DataSet['data']:
              Value = float(Item['values'][Index])
              Y.append(((Value - Tare) * Scale) + Offset)
            if 'label' in MappingChannel and 'name' in MappingChannel['label']:
              Label = MappingChannel['label']['name']
            else:
              Label = 'Channel %d' % (ChannelIndex)
            Color=None
            if 'color' in MappingChannel:
              Color = MappingChannel['color']
            if 'label' in MappingChannel and 'side' in MappingChannel['label'] and MappingChannel['label']['side'] == 'right':
              if not axis2:
                axis2 = axis1.twinx()
              Line, = axis2.plot(X, Y, color=Color, label=Label)
              axis2.set_ylabel(Label)
            else:
              Line, = axis1.plot(X, Y, color=Color, label=Label)
              axis1.set_ylabel(Label)
            Lines.append(Line)
            Labels.append(Label)
      fig.tight_layout()
      fig.canvas.set_window_title("%s %s" % (PROGRAM, VERSION))
      print()
      print('  dataset: %s' % (DataSetFileName))
      print('  mapping: %s' % (MappingFileName))
      xmin, xmax = axis1.get_xlim()
      if 'x-axis' in Mapping and 'ticks' in Mapping['x-axis']:
        axis1.set_xticks(np.round(np.linspace(xmin, xmax, Mapping['x-axis']['ticks']), 2))
      Location = 'center right'
      if 'legend' in Mapping and 'position' in Mapping['legend']:
        Location = Mapping['legend']['position']
      axis1.legend(Lines, Labels, loc=Location)
      if 'view' in Mapping:
        if Mapping['view']:
          plt.show()
      else:
        plt.show()
      if 'outfile' in Mapping:
        fig.savefig(Mapping['outfile'])
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
