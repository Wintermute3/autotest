#!/usr/bin/env python3

#==============================================================================
# perform a sequence of operations on an rd6006 voltage/current source and
# save the resulting dataset to a file.  the rd6006 class also works
# transparently with the rd6012 and rd6018 models.
#==============================================================================

PROGRAM = 'at-u3.py'
VERSION = '2.103.101'
CONTACT = 'bright.tiger@mail.com' # michael nagy

import os, sys, time, json
from pathlib import Path

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

  sudo apt-get install -y libusb-1.0-0-dev
  git clone git://github.com/labjack/exodriver.git
  cd exodriver/
  sudo ./install.sh
  cd ..
  git clone git://github.com/labjack/LabJackPython.git
  cd LabJackPython/
  sudo apt install -y python3-setuptools
  sudo python3 setup.py install

 note: you may have to reboot before the new drivers will see the u3 pod.
'''))
  os._exit(1)

#==============================================================================
# default values
#==============================================================================

InputCount =   4
LoopCount  =  10
LoopDelay  = 100

DefaultOutputFileName    = '%s-output.json' % (PROGRAM.split('.')[0])
DefaultSemaphoreFileName = '%s.go'          % (PROGRAM.split('.')[0])

OutputFileName = DefaultOutputFileName
SemaphoreFileName  = DefaultSemaphoreFileName
ConfigFileName = None

#==============================================================================
# report errors
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

def ShowErrorConfig(Key):
  ShowError("the config file '%s' has an an invalid '%s' section" % (ConfigFileName, Key))

#==============================================================================
# show usage help
#==============================================================================

def ShowHelp():
  HelpText = '''\
    labjack u3-series programmable data-acquisition unit interface.  can perform simple timed
    sequences of reads from various ports, configured in various ways, and write data to a
    file.

usage:

    %s [-h] [-n=1..12] [-t=###] [-l=###]
      [-s=filename] [-c=filename[.json]] [-o=filename[.json]]

where:

    -h . . . . . . this help text
    -n=# . . . . . number of inputs to scan (default %d, range 1..12)
    -t=# . . . . . time between sample loops (milliseconds, default %d)
    -l=# . . . . . number of sample loops (default %d)
    -s=xxxxx . . . name of semaphore file (default '%s')
    -c=xxxxx . . . name of config file (optional)
    -o=xxxxx . . . name of output file (default '%s')
'''
  print(HelpText % (sys.argv[0],
    InputCount, LoopDelay, LoopCount, DefaultSemaphoreFileName, DefaultOutputFileName))
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
    elif arg.startswith('-s='):
      try:
        SemaphoreFileName = arg[3:]
        if len(SemaphoreFileName) < 1:
          ShowErrorToken(arg)
      except:
        ShowErrorToken(arg)
    elif arg.startswith('-c='):
      try:
        ConfigFileName = arg[3:]
        if len(ConfigFileName) < 1:
          ShowErrorToken(arg)
        if not ConfigFileName.endswith('.json'):
          ConfigFileName += '.json'
      except:
        ShowErrorToken(arg)
    elif arg.startswith('-o='):
      try:
        OutputFileName = arg[3:]
        if len(OutputFileName):
          if not OutputFileName.endswith('.json'):
            OutputFileName += '.json'
      except:
        ShowErrorToken(arg)
    else:
      ShowErrorToken(arg)
  else:
    ShowErrorToken(arg)

#==============================================================================
# load configuration from file if available
#==============================================================================

ChannelName   = []
ChannelTare   = []
ChannelScale  = []
ChannelOffset = []
DisplayValues = []

if ConfigFileName:
  try:
    Config = json.load(open(ConfigFileName))
    if 'channels' in Config:
      try:
        for Input, Channel in enumerate(Config['channels']):
          if 'name' in Channel:
            ChannelName.append(Channel['name'])
          else:
            if 'note' in Channel:
              ChannelName.append(Channel['note'])
            else:
              ChannelName.append('input-%d' % (Input))
          if 'tare' in Channel:
            ChannelTare.append(Channel['tare'])
          else:
            ChannelTare.append(0.0)
          if 'scale' in Channel:
            ChannelScale.append(Channel['scale'])
          else:
            ChannelScale.append(1.0)
          if 'offset' in Channel:
            ChannelOffset.append(Channel['offset'])
          else:
            ChannelOffset.append(0.0)
          DisplayValues.append(0.0)
        InputCount = len(Config['channels'])
      except:
        ShowErrorConfig('channels')
    if 'outputfile' in Config:
      OutputFileName = Config['outputfile']
    if 'loop' in Config:
      try:
        if 'delay' in Config['loop']:
          LoopDelay = Config['loop']['delay']
      except:
        ShowErrorConfig('loop.delay')
      try:
        if 'count' in Config['loop']:
          LoopCount = Config['loop']['count']
      except:
        ShowErrorConfig('loop.count')
  except:
    ShowError("config file '%s' not found" % (ConfigFileName))

if not ChannelName:
  for Input in range(0, InputCount):
    ChannelName  .append('input-%d' % (Input))
    ChannelTare  .append(0.0)
    ChannelScale .append(1.0)
    ChannelOffset.append(0.0)
    DisplayValues.append(0.0)

#==============================================================================
# show the active option values
#==============================================================================

if ConfigFileName:
  print('  config file . . . . . %s'            % (ConfigFileName))
  print('   touch file . . . . . %s'            % (SemaphoreFileName ))
  print('  channel names . . . . %s'            % (ChannelName   ))
  print('          tares . . . . %s'            % (ChannelTare   ))
  print('          scales  . . . %s'            % (ChannelScale  ))
  print('          offsets . . . %s'            % (ChannelOffset ))
print('  input count . . . . . %d'              % (InputCount    ))
print('  loop delay  . . . . . %d milliseconds' % (LoopDelay     ))
print('  loop count  . . . . . %d'              % (LoopCount     ))
print('  output file . . . . . %s'              % (OutputFileName))

#==============================================================================
# do the actual sampling
#==============================================================================

print()
LoopDelay = float(LoopDelay) / 1000.0
QuickSample = 1
LongSettling = 0
InputSet = []
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
    Time0 = time.time()
    Time1 = Time0
    Path(SemaphoreFileName).touch()
    print('     time', end='')
    for Input in range(InputCount):
      if ChannelName[Input]:
        Name = ChannelName[Input]
      else:
        Name = '%02d' % (Input)
      print('%10s' % (Name), end='')
    print()
    print('   ------', end='')
    for Input in range(InputCount):
      print('%10s' % ('-' * 8), end='')
    print()
    for Loop in range(LoopCount):
      results = LabJack.getFeedback(FeedbackArguments)
      Summary = ''
      InputValues = []
      for Input in range(InputCount):
        if isHV is True and Input < 4:
          lowVoltage = False # use high voltage calibration
        else:
          lowVoltage = True
        Value = LabJack.binaryToCalibratedAnalogVoltage(results[2 + Input], isLowVoltage=lowVoltage, isSingleEnded=True)
        Value -= ChannelTare  [Input]
        Value *= ChannelScale [Input]
        Value += ChannelOffset[Input]
        InputValues.append(Value)
        #DisplayValues[Input] *=    9.0 / 10.0
        #DisplayValues[Input] +=  Value / 10.0
        #Display = DisplayValues[Input] / 10.0 # smoothing
        #Summary += '%8.3f  ' % (Display)
        Summary += '%8.3f  ' % (Value)
      Time = time.time() - Time0
      if OutputFileName:
        InputSet.append({'time': Time, 'values': InputValues})
      print('   %06.2f  %s' % (Time, Summary), end='\r')
      Time2 = time.time()
      Delay = LoopDelay - (Time2 - Time1)
      time.sleep(Delay)
      Time1 += LoopDelay
    print()
  finally:
    LabJack.close()
except KeyboardInterrupt:
  print()
  pass
except:
  print("*** couldn't find a labjack u3 device - is one plugged in and turned on?")
  print()
  os._exit(1)

if OutputFileName:
  with open(OutputFileName, 'w') as f:
    Channels = []
    for Input in range(InputCount):
      Channels.append(ChannelName[Input])
    DataSet = {
      'channels': Channels,
      'data'    : InputSet
    }
    f.write(json.dumps(DataSet, indent=2))

  print()
  print('done - wrote %d sample sets to %s' % (len(InputSet), OutputFileName))
print()

#==============================================================================
# end
#==============================================================================
