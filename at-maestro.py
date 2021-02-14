#!/usr/bin/env python3

#==============================================================================
# monitor the inputs from a pololu maestro servo controller
#==============================================================================

PROGRAM = 'at-maestro.py'
VERSION = '2.102.131'
CONTACT = 'bright.tiger@mail.com' # michael nagy

import os, sys, struct

print()
print("%s %s" % (PROGRAM, VERSION))
print()

#==============================================================================
# the usb parameters for the pololu maestro mini 12 servo controller
#==============================================================================

VID_POLOLU  = 0x1ffb
PID_MAESTRO = 0x008a # mini maestro 12

SERVO_CHANNELS = 12

SN_CNTBX = '00068800'

#==============================================================================
# various help messages
#==============================================================================

HelpImportUsb = '''\
to fix this sad state of affairs, run the following command and try again:

  pip3 install pyusb
'''

HelpUdevRule = '''\
to fix this sad state of affairs, run the following command:

  echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="%04x", MODE:="0666"' | \\
    sudo tee /etc/udev/rules.d/maestro.rules > /dev/null

then unplug and replug the maestro device and try again
''' % (VID_POLOLU)

#==============================================================================
# fatal error
#==============================================================================

def ShowError(Message, Detail=None):
  print('*** %s!' % (Message))
  print()
  if Detail:
    print('%s' % (Detail))
  os._exit(1)

#==============================================================================
# import the usb library
#==============================================================================

try:
  import usb.core
  import usb.util
except:
  ShowError("the python3 library 'usb' is not installed", HelpImportUsb)
  os._exit(1)

#==============================================================================
# show usage help
#==============================================================================

def ShowHelp():
  HelpText = '''\
    pololu maestro servo control input monitort

usage:

    %s
'''
  print(HelpText % (sys.argv[0]))
  os._exit(1)

#==============================================================================
# find our device
#==============================================================================

Maestro = usb.core.find(idVendor=VID_POLOLU, idProduct=PID_MAESTRO)
if Maestro is None:
  ShowError('maestro device not found')
#print('%s' % (Maestro))
try:
  Serial = usb.util.get_string(Maestro, Maestro.iSerialNumber)
except:
  ShowError('required udev rule missing!', HelpUdevRule)
print('  serial: [%s]' % (Serial))
if Serial != SN_CNTBX:
  print()
  ShowError('unexpected serial number')

#==============================================================================
# scan inputs
#==============================================================================

REQUEST_GET_SERVO_SETTINGS = 0x87

Name = [
   'light-0', 'light-1', 'light-2', 'light-3',
  'button-0','button-1','button-2','button-3',
    'knob-0',  'knob-1',  'knob-2',  'knob-3'
]

Format = 'Hxxxxx'

Settings = Maestro.ctrl_transfer(
  0xC0, REQUEST_GET_SERVO_SETTINGS, 0, 0,
  SERVO_CHANNELS * struct.calcsize(Format)
)

print()
print('  ch      name  value')
print('  --  --------  -----')
for Channel, Vector in enumerate(struct.iter_unpack(Format,Settings)):
  Value = Vector[0]
  print('  %02d  %8s  %04d' % (Channel, Name[Channel], Value))

print()
print('done')
print()

#==============================================================================
# end
#==============================================================================
