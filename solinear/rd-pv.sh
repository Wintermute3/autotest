#!/bin/bash

# pv simulation, 8s ramp to 10v, 5s hold, 8s ramp to 0v

../at-rd6000.py -o=rd-pv.json -i=18927 -s=rd-go v=0,on [v+0.5,s=0.2]=20 s=5 [v-0.5,s=0.2]=20 off
