#!/usr/bin/env python3

#==============================================================================
# catch the datastream from a btmeter and record to a json dataset
#==============================================================================

PROGRAM = 'at-btmeter.py'
VERSION = '2.102.171'
CONTACT = 'bright.tiger@mail.com' # michael nagy

import os, sys, time, json, serial

print()
print("%s %s" % (PROGRAM, VERSION))
print()

#==============================================================================
# show usage help
#==============================================================================

FileName = '.%s.json' % (PROGRAM.split('.')[0])

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
  print('  using multimeter at index %d' % (MeterIndex))
except serial.serialutil.SerialException:
  print("*** you don't have permission to use the serial/usb port.  to fix this")
  print('*** sad state of affairs, first run the following command:')
  print()
  print('  sudo usermod -a -G dialout $USER')
  print()
  print('*** then log off and back on to make the change effective, and try again.')
  print()
  os._exit(1)


#==============================================================================
# the following routines decipher the datastream from the meter, which is in
# the form of 14-byte blocks, transmitted at 2400 baud, approximately twice
# per second.  the first nibble of each byte is the 1-based index in the
# block.  the second nibble positionally-encodes various data as follows:
#
#   index  second nibble
#   -----  -----------------------
#     1    ac/dc indicator
#    2-9   4 display digits
#   10-11  exponent (u, m, K, M or none)
#   12-13  unit (volts, amps, ohms)
#     14   always a 1
#
# digits are encoded by two nibbles each, with the high bit of the resulting
# byte indicating either a minus sign (for the first digit only) or a leading
# decimal (for subsequent digits).  the actual 7-bit encodings of the digits
# are literal mappings of the 7-segment LCD display segments.
#==============================================================================

# eliminate redundant leading zeros and negative signs on zero values

def RemoveLeadingZeros(Reading):
  if Reading.startswith('-'):
    Normalized = RemoveLeadingZeros(Reading[1:])
    for Digit in Normalized:
      if Digit in '123456789':
        return '-' + Normalized
    return Normalized
  while Reading.startswith('0') and len(Reading) > 1:
    if Reading[1:2] in '0123456789':
      Reading = Reading[1:]
    else:
      break
  return Reading

# bitmasks for 7-segment digits:
#
#    ---       10
#   |   |   20    01
#    ---       02
#   |   |   40    04
#    ---       08

def DecodeDigit(Digit):
  if Digit == 0x00:
    raise Exception('Digit $%02x' % Digit) # ' '
  if Digit == 0x68:
    raise Exception('Digit $%02x' % Digit) # 'L'
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
  raise Exception('Digit $%02x' % Digit)

# determine what units to display, and what scale factor to apply, as well
# as the format to use to display the value.  the flags word is 5 digits,
# bit-mapped like this:
#
#   80000 u (micro)
#   20000 K (kilo)
#   08000 m (milli)
#   02000 M (mega)
#   00400 ohm
#   00080 amp
#   00040 volt

def DecodeFlags(Flags):
  if   Flags[2:] == '041':
    Unit = 'Volt'
    Format = '%5.3f'
  elif Flags[2:] == '401':
    Unit = 'Ohm'
    Format = '%3.1f'
  elif Flags[2:] == '081':
    Unit = 'Amp'
    Format = '%5.3f'
  else:
    raise Exception('Unit [%s]' % (Flags[2:]))
  if   Flags [:2] == '00':
    Exponent = 0
  elif Flags [:2] == '02': # M
    Exponent = 6
    Format = '%1.0f'
  elif Flags [:2] == '20': # K
    Exponent = 3
    Format = '%1.0f'
  elif Flags [:2] == '08': # m
    Exponent = -3
    Format = '%7.5f'
  elif Flags [:2] == '80': # u
    Exponent = -6
    Format = '%9.7f'
  else:
    raise Exception('Exponent [%s]' % (Flags[:2]))
  return Unit, Exponent, Format

# determine the meter reading, and return the numeric value, the unit, and
# the best format to display it

def DecodeBuffer(Buffer):
  for Index, Data in enumerate(Buffer):
    Check = (Data // 16) - 1
    if Index != Check:
      raise Exception('Bad Check Nibble')
  Image = ''
  Flags = ''
  AcDc = ''
  for Index, Data in enumerate(Buffer):
    Nibble = Data % 16
    if Index == 0:
      if Nibble == 1:
        pass # Image += 'diode'
      elif Nibble == 3:
        pass # Image += 'Ohms'
      elif Nibble == 7:
        AcDc = 'DC '
      elif Nibble == 11: # 'b'
        AcDc = 'AC '
      else:
        raise Exception('Bad Class Nibble [%x]' % (Nibble))
    elif Index in [1,3,5,7]:
      if Nibble & 0x08:
        if Index == 1:
          Image += '-'
        else:
          Image += '.'
        Nibble &= ~0x08
      Digit = Nibble * 16
    elif Index in [2,4,6,8]:
      Digit += Nibble
      Image += DecodeDigit(Digit)
    else:
      Flags += '%x' % (Nibble)
  Unit, Exponent, Format = DecodeFlags(Flags)
  Value = float(RemoveLeadingZeros(Image)) * pow(10,Exponent)
  Unit = AcDc + Unit
  return Value, Unit, Format

#==============================================================================
# catch the datastream from the meter
#==============================================================================

print('  waiting for data')
Time0 = time.time()
OutputSet = []
Buffer = b''
while True:
  try:
    Data = Meter.read()
    Time1 = time.time()
    TimeX = Time1 - Time0
    if TimeX > 0.100:
      if Buffer:
        try:
          Value, Unit, Format = DecodeBuffer(Buffer)
          if not OutputSet:
            OutputTime = time.time()
            OutputUnit = Unit
            print('  recording data')
            print()
          ValueTime = time.time() - OutputTime
          if OutputUnit == Unit:
            OutputSet.append({'time': '%5.3f' % (ValueTime), 'values': [Format % (Value)]})
          print('  %04d  %05.1f  %15.7f %s    \r' % (len(OutputSet), ValueTime, Value, Unit), end='')
        except KeyboardInterrupt:
          raise
        except:
          #for B in Buffer:
          #  print(' %02x' % (B), end='')
          #print()
          pass
      Buffer = b''
    Buffer += Data
    Time0 = Time1
  except KeyboardInterrupt:
    print('\r  ')
    break

#==============================================================================
# output the captured data to the json datafile
#==============================================================================

with open(FileName, 'w') as f:
  DataSet = {
    'channels': [OutputUnit],
    'data'    :  OutputSet
  }
  f.write(json.dumps(DataSet, indent=2))

#==============================================================================
# sign off
#==============================================================================

print()
print("done - wrote %d sample sets to file: '%s'" % (len(OutputSet), FileName))
print()

#==============================================================================
# end
#==============================================================================
