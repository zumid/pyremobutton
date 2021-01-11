#!/usr/bin/env python3

import os
import sys
from evdev import InputDevice, categorize, ecodes, list_devices

if(len(sys.argv) <= 1):
    print('Error: Need args')
    sys.exit()

MACADDRESS=str(sys.argv[1])

print('Mac address = ', MACADDRESS)

devices = [InputDevice(fn) for fn in list_devices()]

for device in devices:
    print('[Path]',device.path,'[Name]', device.name,'[Uniq]', device.uniq)
    if MACADDRESS in str(device.uniq) and 'Control' in str(device.name):
        print('[find]',device.path)
        target_device_path=device.path
        break

#dev1 = InputDevice('/dev/input/event1')
dev1 = InputDevice(target_device_path)

print(dev1)

dev1.capabilities(verbose=True)

for event in dev1.read_loop():
    if event.type == ecodes.EV_KEY:
        print(categorize(event))
        if 'down' in str(categorize(event)) :
            os.system('/opt/ir/bin/bedroom_light.sh')
   
