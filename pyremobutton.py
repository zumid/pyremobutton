#!/usr/bin/env python3
from __future__ import absolute_import, print_function, unicode_literals

import dbus
import dbus.mainloop.glib
try:
    #from gi.repository import GObject
    from gi.repository import GLib
except ImportError:
    exit()
import os
import sys
import time
from datetime import datetime

from logging import getLogger,INFO,Formatter,StreamHandler,FileHandler

from evdev import InputDevice, categorize, ecodes, list_devices

import multiprocessing as mp

#from monitor_bluetooth import * 

import settings


def main():
    processlist = []
    for button in settings.BUTTON.values():
        p1 = mp.Process(target=read_button_daemon, args=(button,))
        logger.info(p1)
        p1.start()
        processlist.append(p1)
    sys.exit()
 
def read_button_daemon(button):
    global g_button
    g_button = button
    logger.info("Child Process Start:NAME=%s MAC=%s COMMAND=%s",g_button['NAME'],g_button['MAC'],g_button['COMMAND'])
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    bus.add_signal_receiver(find_connection, bus_name="org.bluez",
                    dbus_interface="org.freedesktop.DBus.Properties",
                    signal_name="PropertiesChanged",
                    path_keyword="path")
    mainloop = GLib.MainLoop()
    logger.info("Start {}".format(g_button['NAME']))
    try:
        mainloop.run()
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt {}".format(g_button['NAME']))
        sys.exit()

def child_process(button):
    pid = os.getpid()
    logger.info("{} event start".format(pid))
    COMMAND = button['COMMAND']
    devices = [InputDevice(fn) for fn in list_devices()]
    device = ''
    logger.info("%s,%s,%s",pid,button['NAME'],button['MAC'])
    for device in devices:
        #logger.info(pid,'[Path]',device.path,'[Name]', device.name,'[Uniq]', device.uniq)
        if button['MAC'] in str(device.uniq) and 'Control' in str(device.name):
            logger.info("%s [find] %s",pid,device.path)
            target_device_path=device.path
            break
    del devices
    del device
    dev = InputDevice(target_device_path)
    dev.capabilities(verbose=True)
    try:
        for event in dev.read_loop():
            if event.type == ecodes.EV_KEY:
                logger.info(categorize(event))
                if 'down' in str(categorize(event)) :
                    logger.info("%s %s",pid,"down is pused")
                    os.system(COMMAND)
    except KeyboardInterrupt:
        logger.warning("KeyBoardInterrupt Child")
        sys.exit()
    sys.exit() 

def find_connection(interface, changed, invalidated, path):
    global g_button
    global g_event_process
    iface = interface[interface.rfind(".") + 1:]
    logger.info("iface={} path={}".format(iface,path))
    path2 = path.replace('_',':')
    logger.info("path2={} MAC={}".format(path2,g_button['MAC']))
    for name, value in changed.items():
        val = str(value)
        logger.info("{%s.PropertyChanged} [%s] %s = %s" % (iface, path, name,val))
        if g_button['MAC'] in path2 and name == "Connected" and val == "1":
            logger.info("[FIND] {}".format(g_button['NAME']))
            os.system(g_button['COMMAND'])
            g_event_process = mp.Process(target=child_process, args=(g_button,))
            g_event_process.start()
            logger.debug("##########################")
        elif g_button['MAC'] in path2 and name == "Connected" and val == "0":
            try:
                g_event_process.terminate()
            except NameError:
                logger.warning("g_event_process terminate failed")
                pass

if __name__ == '__main__':
    g_button = ''
    g_event_process = ''
    
    prog_name = os.path.splitext(os.path.basename(__file__))[0]

    # Logger setting
    logger = getLogger(__name__)
    
    # フォーマット
    log_format = Formatter("%(asctime)s [%(levelname)8s] %(message)s")
    # レベル
    logger.setLevel(INFO)

    # 標準出力へのハンドラ
    stdout_handler = StreamHandler(sys.stdout)
    stdout_handler.setFormatter(log_format)
    logger.addHandler(stdout_handler)
    # ログファイルへのハンドラ
    file_handler = FileHandler("./log/"+prog_name+"_"+datetime.now().strftime("%Y%m%d")+".log")
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    a="text"

    main()

