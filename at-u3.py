#!/usr/bin/env python3

# todo: revoke dialout group membership and test failure mode reporting

#==============================================================================
# perform a sequence of operations on an rd6006 voltage/current source and
# save the resulting dataset to a file.  the rd6006 class also works
# transparently with the rd6012 and rd6018 models.
#==============================================================================

PROGRAM = 'at-u3.py'
VERSION = '2.102.121'
CONTACT = 'bright.tiger@mail.com' # michael nagy

import os, sys, time, json

print()
print("%s %s" % (PROGRAM, VERSION))
print()

#==============================================================================
# the u3 class is provided by labjack
#==============================================================================

try:
  import u3
except:
  print('%s' % ( '''\
*** the python3 library 'u3' is not installed.  to fix this sad state of
*** affairs, run the following commands and try again:

  git clone git://github.com/labjack/exodriver.git
  cd exodriver/
  sudo ./install.sh
  cd ..
  git clone git://github.com/labjack/LabJackPython.git
  cd LabJackPython/
  sudo python3 setup.py install
'''))
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
# default values
#==============================================================================

InputCount =   4
LoopCount  =  10
LoopDelay  = 100
FileName   = '%s.dat' % (PROGRAM.split('.')[0])

#==============================================================================
# show usage help
#==============================================================================

def ShowHelp():
  HelpText = '''\
    labjack u3-series programmable data-acquisition unit interface.  can perform simple timed
    sequences of reads from various ports, configured in various ways, and write data to a
    file.

usage:

    %s [-h] [-n=1..12] [-t=###] [-l=###] [-f=filename[.dat]]

where:

    -h . . . . . . this help text
    -n=# . . . . . number of inputs to scan (default %d, range 1..12)
    -t=# . . . . . time between sample loops (milliseconds, default %d)
    -l=# . . . . . number of sample loops (default %d)
    -f=xxxx  . . . name of output file (default '%s')
'''
  print(HelpText % (sys.argv[0], InputCount, LoopDelay, LoopCount, FileName))
  os._exit(1)

#==============================================================================
# parse arguments and build token list.  each token is an [opcode,parameter]
# tuple where the the parameter may be None
#==============================================================================

for arg in sys.argv[1:]:
  if arg.startswith('-'):
    if arg == '-h':
      ShowHelp()
    elif arg.startswith('-n='):
      try:
        InputCount = int(arg[3:])
        if InputCount < 1 or InputCount > 12:
          ShowErrorToken(arg)
      except:
        ShowErrorToken(arg)
    elif arg.startswith('-l='):
      try:
        LoopCount = int(arg[3:])
        if LoopCount < 1:
          ShowErrorToken(arg)
      except:
        ShowErrorToken(arg)
    elif arg.startswith('-t='):
      try:
        LoopDelay = int(arg[3:])
        if LoopDelay < 1:
          ShowErrorToken(arg)
      except:
        ShowErrorToken(arg)
    elif arg.startswith('-f='):
      try:
        FileName = arg[3:]
        if len(FileName) < 1:
          ShowErrorToken(arg)
        if not '.' in FileName:
          FileName += '.dat'
      except:
        ShowErrorToken(arg)
    else:
      ShowErrorToken(arg)
  else:
    ShowErrorToken(arg)

#==============================================================================
# show the active option values
#==============================================================================

print('  input count  . . . %d'              % (InputCount))
print('  loop delay . . . . %d milliseconds' % (LoopDelay))
print('  loop count . . . . %d'              % (LoopCount))
print('  filename . . . . . %s'              % (FileName))

#==============================================================================
# do the actual sampling
#==============================================================================

print()
print('final input vector:')
print()

LoopDelay = float(LoopDelay) / 1000.0
QuickSample = 1
LongSettling = 0
InputSet = []
InputValues = [0] * InputCount
Time0 = time.time()
try:
  LabJack = u3.U3()
  LabJack.getCalibrationData()
  try:
    FIOEIOAnalog = (2 ** InputCount) - 1
    fios = FIOEIOAnalog & 0xFF
    eios = FIOEIOAnalog // 256
    LabJack.configIO(FIOAnalog=fios, EIOAnalog=eios)
    LabJack.getFeedback(u3.PortDirWrite(Direction=[0, 0, 0], WriteMask=[0, 0, 15]))
    FeedbackArguments = []
    FeedbackArguments.append(u3.DAC0_8(Value=125))
    FeedbackArguments.append(u3.PortStateRead())
    if LabJack.configU3()['VersionInfo'] & 18 == 18:
      isHV = True # U3 is an HV
    else:
      isHV = False
    for Input in range(InputCount):
      FeedbackArguments.append(u3.AIN(Input, 31, QuickSample=QuickSample, LongSettling=LongSettling))
    for Loop in range(LoopCount):
      results = LabJack.getFeedback(FeedbackArguments)
      for Input in range(InputCount):
        if isHV is True and Input < 4:
          lowVoltage = False # use high voltage calibration
        else:
          lowVoltage = True
        InputValues[Input] = LabJack.binaryToCalibratedAnalogVoltage(results[2 + Input], isLowVoltage=lowVoltage, isSingleEnded=True)
      Time = time.time() - Time0
      InputSet.append({'time': Time, 'values': InputValues})
      time.sleep(LoopDelay)
    Summary = ''
    for Input in range(InputCount):
      Summary += '%6.3f  ' % (InputValues[Input])
    print(' %s' % Summary)
  finally:
    LabJack.close()
except:
  print("*** couldn't find a labjack u3 device - is one plugged in and turned on?")
  print()
  os._exit(1)
  print("*** you don't have permission to use the serial/usb port.  to fix this")
  print('*** sad state of affairs, first run the following command:')
  print()
  print('  sudo usermod -a -G dialout $USER')
  print()
  print('*** then log off and back on to make the change effective, and try again.')
  print()
  os._exit(1)

with open(FileName, 'w') as f:
  Channels = []
  for Input in range(InputCount):
    Channels.append('input-%d' % Input)
  DataSet = {
    'channels': Channels,
    'data'    : InputSet
  }
  f.write(json.dumps(DataSet, indent=2))

print()
print('done - wrote %d sample sets to %s' % (len(InputSet), FileName))
print()

#==============================================================================
# end
#==============================================================================
