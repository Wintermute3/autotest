#!/usr/bin/env python3

#==============================================================================
# catch the datastream from a btmeter and record to a json dataset
#==============================================================================

PROGRAM = 'at-btmeter.py'
VERSION = '2.102.141'
CONTACT = 'bright.tiger@mail.com' # michael nagy

import os, sys, time, json, serial

print()
print("%s %s" % (PROGRAM, VERSION))
print()

#==============================================================================
# show usage help
#==============================================================================

FileName = '%s.dat' % (PROGRAM.split('.')[0])

def ShowHelp():
  HelpText = '''\
    btmeter connect multimeter data aquisition

usage:

    %s [-h] [-i=1/2/3/4...] [-f=filename[.dat]]

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
# validate an integer or float command or throw an error.  also set a globel
# as a side-effect.
#==============================================================================

Integer = 0

def ValidInteger(Command, Length):
  global Integer
  if len(Command) > Length:
    try:
      Integer = int(Command[Length:])
    except:
      ShowErrorToken(Command)
  else:
    ShowErrorToken(Command)
  return Command

Float = 0.0

def ValidFloat(Command, Length):
  global Float
  if len(Command) > Length:
    try:
      Float = float(Command[Length:])
    except:
      ShowErrorToken(Command)
  else:
    ShowErrorToken(Command)
  return Command

#==============================================================================
# helper for option recognition
#==============================================================================

def StartsWithAny(Option, Prefixes, Length):
  if len(Option) > Length:
    if Option[:Length] in Prefixes:
      return True
  else:
    ShowErrorToken(Option)
  return False

#==============================================================================
# parse arguments
#==============================================================================

MeterIndex = 1

Tokens = []
Depth = 0
for arg in sys.argv[1:]:
  if arg.startswith('-'):
    if Tokens:
      ShowErrorToken(arg) # options must come before commands
    else:
      if arg == '-h':
        ShowHelp()
      elif arg.startswith('-i='):
        try:
          MeterIndex = int(arg[3:])
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
# get access to a specific multimeter
#==============================================================================

import serial.tools.list_ports

Ports = []

for Port in list(serial.tools.list_ports.comports()):
  if "VID:PID=067B:2303" in Port[2]:
    Ports.append(Port[0])

print('  found %d multimeters' % (len(Ports)))
if not len(Ports):
  print()
  print("*** unable to find a multimeter - is one plugged in and turned on?")
  print()
  os._exit(1)

if len(Ports) < MeterIndex:
  print()
  print("*** multimeter index %d out of range" % (MeterIndex))
  print()
  os._exit(1)

BaudRate = 2400
ChunkSize = 14

try:
  Meter = serial.Serial(Ports[MeterIndex-1], BaudRate, timeout=1)
  print('  found a btmeter at index %d' % (MeterIndex))
except serial.serialutil.SerialException:
  print("*** you don't have permission to use the serial/usb port.  to fix this")
  print('*** sad state of affairs, first run the following command:')
  print()
  print('  sudo usermod -a -G dialout $USER')
  print()
  print('*** then log off and back on to make the change effective, and try again.')
  print()
  os._exit(1)

print()
Time0 = time.time()
OutputSet = []
print('baudrate: %d' % (BaudRate))

# first nibble of each byte is index in chunk 1..14
# second nibble carries data:
#
#                        mode  read  units
#                        ----- ----- -----
# 7 7d 7d 7d fd 08041    Volts 000.0 mv
# 3 7d 7d 7d fd 00401    Ohms  000.0 Ohms
# 7 7d 3e a7 7f 00041    Volts 05.48 V
# 7 7d 1f ff 3f 00041          03.89
# 7 7d 1f bf 7d 00041          03.90
# 7 7d 1f 95 7e 00041          03.76
# 7 5b 85 3e 5b 00041          2.152
# 7 05 bf 5b 27 00041          1.924 V
# 342.0         08041          342.0 mv


def DecodeDigit(Digit):
  if Digit == 0x7d:
    return '0'
  if Digit == 0x05:
    return '1'
  if Digit == 0x5b:
    return '2'
  if Digit == 0x1f:
    return '3'
  if Digit == 0x27:
    return '4'
  if Digit == 0x3e:
    return '5'
  if Digit == 0x7e:
    return '6'
  if Digit == 0x15:
    return '7'
  if Digit == 0x7f:
    return '8'
  if Digit == 0x3f:
    return '9'
  return '#'

def DecodeBuffer(Buffer):
  for Index, Data in enumerate(Buffer):
    Check = (Data // 16) - 1
    if Index != Check:
      return '*'
  Image = ''
  for Index, Data in enumerate(Buffer):
    Nibble = Data % 16
    if Index == 0:
      if Nibble == 7:
        Image += 'Volts '
      else:
        Image += '? '
    elif Index in [1,3,5,7]:
      if Nibble & 0x08:
        Image += '.'
        Nibble &= ~0x08
      Digit = Nibble * 16
    elif Index in [2,4,6,8]:
      Digit += Nibble
      Image += DecodeDigit(Digit)
    else:
      if Index == 9:
        Image += ' '
      Image += '%x' % (Nibble)
  return Image

Buffer = b''
while True:
  Data = Meter.read()
  Time1 = time.time()
  TimeX = Time1 - Time0
  if TimeX > 0.100:
    if Buffer:
      Image = DecodeBuffer(Buffer)
      print('  %s' % (Image))
    Buffer = b''
  Buffer += Data
  Time0 = Time1

with open(FileName, 'w') as f:
  DataSet = {
    'channels': ['volts','amps'],
    'data'    : OutputSet
  }
  f.write(json.dumps(DataSet, indent=2))

print()
print('done - wrote %d sample sets to %s' % (len(OutputSet), FileName))
print()

#==============================================================================
# end
#==============================================================================
