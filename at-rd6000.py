#!/usr/bin/env python3

#==============================================================================
# perform a sequence of operations on an rd6006 voltage/current source and
# save the resulting dataset to a file.  the rd6006 class also works
# transparently with the rd6012 and rd6018 models.
#==============================================================================

PROGRAM = 'at-rd6000.py'
VERSION = '2.102.111'
CONTACT = 'bright.tiger@mail.com' # michael nagy

import os, sys, time
import datetime as dt

print()
print("%s %s" % (PROGRAM, VERSION))
print()

#==============================================================================
# the RD6006 class has been adapted, with minor tweeks, from the repository:
#
#   https://github.com/Baldanos/rd6006.git
#
# to install it directly, conventionally:
#
#   git clone https://github.com/Baldanos/rd6006.git
#   cd rd6006/
#   python3 setup.py install --user
#==============================================================================

try:
  import minimalmodbus
except:
  print("*** the python3 library 'minimalmodbus' is not installed.  to fix this")
  print('*** sad state or affairs, run the following command and try again:')
  print()
  print('  pip3 install minimalmodbus')
  print()
  os._exit(1)


minimalmodbus.TIMEOUT = 0.5

class RD6006:
  def __init__(self, port, address=1, baudrate=115200):
    self.port = port
    self.address = address
    self.instrument = minimalmodbus.Instrument(port=port, slaveaddress=address)
    self.instrument.serial.baudrate = baudrate
    regs = self._read_registers(0, 4)
    self.sn = regs[1] << 16 | regs[2]
    self.fw = regs[3] / 100
    self.type = int(regs[0] / 10)
    self.voltres = 100

    if self.type == 6012 or self.type == 6018:
      self.ampres = 100 # RD6012 or RD6018
    else:
      self.ampres = 1000 # RD6006 or other

  def __repr__(self):
    return f"RD6006 SN:{self.sn} FW:{self.fw}"

  def _read_register(self, register):
    try:
        return self.instrument.read_register(register)
    except minimalmodbus.NoResponseError:
        return self._read_register(register)

  def _read_registers(self, start, length):
    try:
      return self.instrument.read_registers(start, length)
    except minimalmodbus.NoResponseError:
      return self._read_registers(start, length)
    except minimalmodbus.InvalidResponseError:
      return self._read_registers(start, length)

  def _write_register(self, register, value):
    try:
      return self.instrument.write_register(register, value)
    except minimalmodbus.NoResponseError:
      return self._write_register(register, value)

  def _mem(self, M=0):
    """reads the 4 register of a Memory[0-9] and print on a single line"""
    regs = self._read_registers(M * 4 + 80, 4)
    print(
      f"M{M}: {regs[0] / self.voltres:4.1f}V, {regs[1] / self.ampres:3.3f}A, OVP:{regs[2] / self.voltres:4.1f}V, OCP:{regs[3] / self.ampres:3.3f}A"
    )

  def status(self):
    regs = self._read_registers(0, 84)
    print("== Device")
    print(f"Model   : {regs[0]/10}")
    print(f"SN      : {(regs[1]<<16 | regs[2]):08d}")
    print(f"Firmware: {regs[3]/100}")
    print(f"Input   : {regs[14] / self.voltres}V")
    if regs[4]:
      sign = -1
    else:
      sign = +1
    print(f"Temp    : {sign * regs[5]}°C")
    if regs[34]:
      sign = -1
    else:
      sign = +1
    print(f"TempProb: {sign * regs[35]}°C")
    print("== Output")
    print(f"Voltage : {regs[10] / self.voltres}V")
    print(f"Current : {regs[11] / self.ampres}A")
    print(f"Energy  : {regs[12]/1000}Ah")
    print(f"Power   : {regs[13]/100}W")
    print("== Settings")
    print(f"Voltage : {regs[8] / self.voltres}V")
    print(f"Current : {regs[9] / self.ampres}A")
    print("== Protection")
    print(f"Voltage : {regs[82] / self.voltres}V")
    print(f"Current : {regs[83] / self.ampres}A")
    print("== Battery")
    if regs[32]:
      print("Active")
      print(f"Voltage : {regs[33] / self.voltres}V")
    print(
      f"Capacity: {(regs[38] <<16 | regs[39])/1000}Ah"
    )  # TODO check 8 or 16 bits?
    print(
      f"Energy  : {(regs[40] <<16 | regs[41])/1000}Wh"
    )  # TODO check 8 or 16 bits?
    print("== Memories")
    for m in range(10):
      self._mem(M=m)

  @property
  def input_voltage(self):
    return self._read_register(14) / self.voltres

  @property
  def voltage(self):
    return self._read_register(8) / self.voltres

  @property
  def meastemp_internal(self):
    if self._read_register(4):
      return -1 * self._read_register(5)
    else:
      return 1 * self._read_register(5)

  @property
  def meastempf_internal(self):
    if self._read_register(6):
      return -1 * self._read_register(7)
    else:
      return 1 * self._read_register(7)

  @property
  def meastemp_external(self):
    if self._read_register(34):
      return -1 * self._read_register(35)
    else:
      return 1 * self._read_register(35)

  @property
  def meastempf_external(self):
    if self._read_register(36):
      return -1 * self._read_register(37)
    else:
      return 1 * self._read_register(37)

  @voltage.setter
  def voltage(self, value):
    self._write_register(8, int(value * self.voltres))

  @property
  def measvoltage(self):
    return self._read_register(10) / self.voltres

  @property
  def meascurrent(self):
    return self._read_register(11) / self.ampres

  @property
  def measpower(self):
    return self._read_register(13) / 100

  @property
  def measah(self):
    return (
      self._read_register(38) << 16 | self._read_register(39)
    ) / 1000  # TODO check 16 or 8 bit

  @property
  def measwh(self):
    return (
      self._read_register(40) << 16 | self._read_register(41)
    ) / 1000  # TODO check 16 or 8 bit

  @property
  def battmode(self):
    return self._read_register(32)

  @property
  def battvoltage(self):
    return self._read_register(33)

  @property
  def current(self):
    return self._read_register(9) / self.ampres

  @current.setter
  def current(self, value):
    self._write_register(9, int(value * self.ampres))

  @property
  def voltage_protection(self):
    return self._read_register(82) / self.voltres

  @voltage_protection.setter
  def voltage_protection(self, value):
    self._write_register(82, int(value * self.voltres))

  @property
  def current_protection(self):
    return self._read_register(83) / self.ampres

  @current_protection.setter
  def current_protection(self, value):
    self._write_register(83, int(value * self.ampres))

  @property
  def enable(self):
    return self._read_register(18)

  @enable.setter
  def enable(self, value):
    self._write_register(18, int(value))

  @property
  def ocpovp(self):
    return self._read_register(16)

  @property
  def CVCC(self):
    return self._read_register(17)

  @property
  def backlight(self):
    return self._read_register(72)

  @backlight.setter
  def backlight(self, value):
    self._write_register(72, value)

  @property
  def date(self):
    """returns the date as tuple: (year, month, day)"""
    regs = self._read_registers(48, 3)
    year = regs[0]
    month = regs[1]
    day = regs[2]
    return (year, month, day)

  @date.setter
  def date(self, value):
    """Sets the date, needs tuple with (year, month, day) as argument"""
    year, month, day = value
    self._write_register(48, year)
    self._write_register(49, month)
    self._write_register(50, day)

  @property
  def time(self):
    """returns the time as tuple: (h, m, s)"""
    regs = self._read_registers(51, 3)
    h = regs[0]
    m = regs[1]
    s = regs[2]
    return (h, m, s)

  @time.setter
  def time(self, value):
    """sets the time, needs time with (h, m, s) as argument"""
    h, m, s = value
    self._write_register(51, h)
    self._write_register(52, m)
    self._write_register(53, s)

#==============================================================================
# show usage help
#==============================================================================

def ShowHelp():
  HelpText = '''\
    riden rd6000-series programmable power-supply control.  can perform simple timed
    sequences of voltage and current settings, as well as turn the supply on and off.

usage:

    %s [-h] [-i=1/2/3/4...] command {command {command...}}

where:

    -h . . . . . . this help text
    -i=# . . . . . specify power supply index (default 1)
    command  . . . command, as listed below (repeat as desired)

if more than one power supply, select the desired one by supplying an integer
index, 1 for the first one, 2 for the second one, etc.

commands may be any of:

    on  . . . . . . turn supply on
    off . . . . . . turn supply off

    [ . . . . . . . open group
    ]=# . . . . . . close group and repeat (integer)

    s=### . . . . . delay seconds (float)
    m=### . . . . . delay milliseconds (integer)

    c=### . . . . . set current (float, amps)
    c+### . . . . . step up current (float, amps)
    c-### . . . . . step down current (float, amps)

    v=### . . . . . set voltage (float, volts)
    v+### . . . . . step up voltage (float, volts)
    v-### . . . . . step down voltage (float, volts)

    ovp=### . . . . set over-voltage protection limit (float, volts)
    ocp=### . . . . set over-current protection limit (float, volts)

commands may also be concatenated and separated by commas or colons, allowing
a more compact notation.  for example, this command sequence sets to voltage
to zero, turns the supply on, ramps the voltage from zero to 5 volts in 10 steps
of 500mv at a rate of one step per second, then turns the supply off:

  v=0,on,[v+0.5,s=1]=10,off

note that groups can be nested, allowing for some complex sequences.
'''
  print(HelpText % (sys.argv[0]))
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
# validate an integer or float command or throw an error
#==============================================================================

def ValidInteger(Command, Length):
  if len(Command) > Length:
    try:
      i = int(Command[Length:])
    except:
      ShowErrorToken(Command)
  else:
    ShowErrorToken(Command)
  return Command

def ValidFloat(Command, Length):
  if len(Command) > Length:
    try:
      f = float(Command[Length:])
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
# split on commas and also consider [ to be both a delimiter and a token
#==============================================================================

def TokenSplit(String):
  tx = []

  token = ''
  for c in String:
    if c == ',':
      if token:
        tx.append(token)
      token = ''
    elif c == '[':
      if token:
        tx.append(token)
      token = ''
      tx.append('[')
    elif c == ']':
      if token:
        tx.append(token)
      token = c
    else:
      token += c
  if token:
    tx.append(token)
  return tx

#==============================================================================
# parse arguments
#==============================================================================

SupplyIndex = 1
Commands = []
Depth = 0
for arg in sys.argv[1:]:
  if arg.startswith('-'):
    if Commands:
      ShowErrorToken(arg) # options must come before commands
    else:
      if arg == '-h':
        ShowHelp()
      elif arg.startswith('-i='):
        try:
          SupplyIndex = int(arg[3:])
        except:
          ShowErrorToken(arg)
      else:
        ShowErrorToken(arg)
  else:
    for a2 in TokenSplit(arg): # .split(','):
      if a2 in ['on','off']:
        Commands.append(a2)
      elif a2 == '[':
        Depth += 1
        Commands.append(a2)
      elif StartsWithAny(a2, [']='], 2):
        Depth -= 1
        Commands.append(ValidInteger(a2, 2))
      elif StartsWithAny(a2, ['m='], 2):
        Commands.append(ValidInteger(a2, 2))
      elif StartsWithAny(a2, ['s=','c=','c+','c-','v=','v+','v-'], 2):
        Commands.append(ValidFloat(a2, 2))
      elif StartsWithAny(a2, ['ovp=','ocp='], 4):
        Commands.append(ValidFloat(a2, 4))
      else:
        ShowErrorToken(a2)

if not Depth == 0:
  ShowError('mismatched [ and ] group indicators')

#==============================================================================
# get access to a specific rd6006 programmable power supply
#==============================================================================

import serial.tools.list_ports

Ports = []

for Port in list(serial.tools.list_ports.comports()):
  if "VID:PID=1A86:7523" in Port[2]:
    Ports.append(Port[0])

print('found %d power supplies' % (len(Ports)))
if not len(Ports):
  print()
  print("*** unable to find a power supplies - is one plugged in and turned on?")
  print()
  os._exit(1)

if len(Ports) < SupplyIndex:
  print()
  print("*** power supply index %d out of range" % (SupplyIndex))
  print()
  os._exit(1)

try:
  r = RD6006(Ports[SupplyIndex-1])
  print('found an rd%d at index %d' % (r.type, SupplyIndex))
except serial.serialutil.SerialException:
  print("*** you don't have permission to use the serial/usb port.  to fix this")
  print('*** sad state or affairs, first run the following command:')
  print()
  print('  sudo usermod -a -G dialout $USER')
  print()
  print('*** then log off and back on to make the change effective, and try again.')
  print()
  os._exit(1)

if Commands:
  for Command in Commands:
    print('%s' % (Command))
else:
  print('no commands, nothing to do')

print()

#==============================================================================
# end
#==============================================================================
