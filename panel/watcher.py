#!/usr/bin/env python3

#==============================================================================
# perform a sequence of operations on an rd6006 voltage/current source and
# save the resulting dataset to a file.  the rd6006 class also works
# transparently with the rd6012 and rd6018 models.
#==============================================================================

PROGRAM = 'watcher.py'
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
# initialize communication with u3
#==============================================================================

InputCount = 7
InputShow = 2
try:
#  LabJack = u3.U3()
#  LabJack.getCalibrationData()
  FIOEIOAnalog = (2 ** InputCount) - 1
  fios = FIOEIOAnalog & 0xFF
  eios = FIOEIOAnalog // 256
#  LabJack.configIO(FIOAnalog=fios, EIOAnalog=eios)
#  LabJack.getFeedback(u3.PortDirWrite(Direction=[0, 0, 0], WriteMask=[0, 0, 15]))
  FeedbackArguments = []
#  FeedbackArguments.append(u3.DAC0_8(Value=125))
#  FeedbackArguments.append(u3.PortStateRead())
#  if LabJack.configU3()['VersionInfo'] & 18 == 18:
#    isHV = True # U3 is an HV
#  else:
#    isHV = False
#  for Input in range(InputCount):
#    FeedbackArguments.append(u3.AIN(Input, 31, QuickSample=QuickSample, LongSettling=LongSettling))
#  for Loop in range(LoopCount):
#    results = LabJack.getFeedback(FeedbackArguments)
#  finally:
#    LabJack.close()
except:
  print("*** couldn't find a labjack u3 device - is one plugged in and turned on?")
  print()
  os._exit(1)

#==============================================================================
# Create figure for plotting
#==============================================================================

import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
xs = []
ys = []

#==============================================================================
# This function is called periodically from FuncAnimation
#==============================================================================

import random

def animate(i, xs, ys):

  # get a reading from the u3
#  if isHV is True and InputShow < 4:
#    lowVoltage = False # use high voltage calibration
#  else:
#    lowVoltage = True
#  Value = LabJack.binaryToCalibratedAnalogVoltage(results[2 + InputShow], isLowVoltage=lowVoltage, isSingleEnded=True)
  Value = random.random() * 20.0

  # Add x and y to lists
  xs.append(len(xs))
  ys.append(Value)

  # Limit x and y lists to 20 items
  xs = xs[-20:]
  ys = ys[-20:]

  # Draw x and y lists
  ax.clear()
  ax.plot(xs, ys)

  # Format plot
#  plt.xticks(rotation=45, ha='right')
#  plt.subplots_adjust(bottom=0.30)
  plt.title('u3 input %d' % (InputShow))
# plt.ylabel('voltage')

#==============================================================================
# Set up plot to call animate() function periodically
#==============================================================================

ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=1000)
plt.show()

#==============================================================================
# end
#==============================================================================
