#!/usr/bin/env python3
from __future__ import absolute_import, print_function, unicode_literals

import dbus
import dbus.mainloop.glib
try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject

import os
import sys
import time

from logging import getLogger,INFO,Formatter

from evdev import InputDevice, categorize, ecodes, list_devices

import multiprocessing as mp

from monitor_bluetooth import * 

import settings


def main():
    processlist = []
    for button in settings.BUTTON.values():
        p1 = mp.Process(target=read_button_daemon, args=(button,))
        print(p1)
        p1.start()
        processlist.append(p1)
    sys.exit()
 
def read_button_daemon(button):
    global g_button
    g_button = button
    print("Child Process Start:NAME=",g_button['NAME'],"MAC=",g_button['MAC'],"COMMAND=",g_button['COMMAND'])
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    bus.add_signal_receiver(find_connection, bus_name="org.bluez",
                    dbus_interface="org.freedesktop.DBus.Properties",
                    signal_name="PropertiesChanged",
                    path_keyword="path")
    mainloop = GObject.MainLoop()
    mainloop.run()

def child_process(button):
    pid = os.getpid()
    print(pid,"#event start")
    COMMAND = button['COMMAND']
    devices = [InputDevice(fn) for fn in list_devices()]
    device = ''
    print(pid,button['NAME'],button['MAC'])
    for device in devices:
        #print(pid,'[Path]',device.path,'[Name]', device.name,'[Uniq]', device.uniq)
        if button['MAC'] in str(device.uniq) and 'Control' in str(device.name):
            print(pid,'[find]',device.path)
            target_device_path=device.path
            break
    del devices
    del device
    dev = InputDevice(target_device_path)
    dev.capabilities(verbose=True)

    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY:
            print(categorize(event))
            if 'down' in str(categorize(event)) :
                print(pid,"down is pused")
                os.system(COMMAND)
    sys.exit() 

def find_connection(interface, changed, invalidated, path):
    global g_button
    global g_event_process

    iface = interface[interface.rfind(".") + 1:]
    print("iface=",iface," path=",path)
    path2 = path.replace('_',':')
    print("path2=",path2,"MAC=",g_button['MAC'])
    for name, value in changed.items():
        val = str(value)
        print("{%s.PropertyChanged} [%s] %s = %s" % (iface, path, name,val))
        if g_button['MAC'] in path2 and name == "Connected" and val == "1":
            print("FIND",g_button['NAME'])
            os.system(g_button['COMMAND'])
            g_event_process = mp.Process(target=child_process, args=(g_button,))
            g_event_process.start()
        elif g_button['MAC'] in path2 and name == "Connected" and val == "0":
            try:
                g_event_process.terminate()
            except NameError:
                pass

if __name__ == '__main__':
    g_button = ''
    g_event_process = ''
    """
    # Logger setting
    logger = getLogger(__name__)
    
    # フォーマット
    log_format = Formatter("%(asctime)s [%(levelname)8s] %(message)s")
    # レベル
    logger.setLevel(INFO)

    # 標準出力へのハンドラ
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(log_format)
    logger.addHandler(stdout_handler)
    # ログファイルへのハンドラ
    file_handler = logging.FileHandler("./log/log.log")
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    """
    main()

'''
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
            print("down is pused")
           # os.system('/opt/ir/bin/bedroom_light.sh')
'''
