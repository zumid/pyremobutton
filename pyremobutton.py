#!/usr/bin/env python3
from __future__ import absolute_import, print_function, unicode_literals

import dbus
import dbus.mainloop.glib
try:
    from gi.repository import GLib
except ImportError:
    exit()
import os
import sys
import time
from datetime import datetime
from logging import getLogger,Formatter,StreamHandler,FileHandler,INFO,DEBUG
from evdev import InputDevice, categorize, ecodes, list_devices

import threading
import subprocess

try:
    import settings
except ModuleNotFoundError:
    import settings_sample as settings


def main():
    thread = {}
    for button in settings.button_setting:
        thread[button['name']] = threading.Thread(target=key_event_monitor,name=button['name'],args=(button,))
        thread[button['name']].setDaemon(True)
        thread[button['name']].start()

    connection_monitor()

    sys.exit()
 
def connection_monitor():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    bus.add_signal_receiver(find_connection, bus_name="org.bluez",
                    dbus_interface="org.freedesktop.DBus.Properties",
                    signal_name="PropertiesChanged",
                    path_keyword="path")
    mainloop = GLib.MainLoop()
    logger.info(f"commection monitor start.")
    try:
        mainloop.run()
    except KeyboardInterrupt:
        logger.warning(f"KeyboardInterrupt of main loop")
        sys.exit()

def key_event_monitor(button):
    devices = [InputDevice(fn) for fn in list_devices()]
    device = ''
    target_device_path=''
    logger.info(f"[{button['name']}] MAC={button['mac']}")
    for device in devices:
        if button['mac'] in str(device.uniq) and 'Control' in str(device.name):
            logger.info(f"[{button['name']}] InputDevice found. path={device.path}")
            target_device_path=device.path
            break
    del devices
    del device

    if not target_device_path:
        logger.warning(f"{button['name']} {button['mac']} was not found on the InputDevice. thread terminated.")
        return

    dev = InputDevice(target_device_path)
    dev.capabilities(verbose=True)
    try:
        for event in dev.read_loop():
            if event.type == ecodes.EV_KEY:
                logger.debug(f"[{button['name']}] [categorize event] {categorize(event)}")
                if event.value == 1:    # key down
                    start_time = time.perf_counter()
                elif event.value == 0:  # key up
                    pushed_time = time.perf_counter() - start_time
                    if (pushed_time < button['long_pushed_time']):
                        pushed='short_pushed'
                        logger.debug(f"short push {pushed_time}")
                        if 'KEY_VOLUMEUP' in str(categorize(event)) :
                            run_command = button['command']['ios_button']
                        elif 'KEY_ENTER' in str(categorize(event)):
                            run_command = button['command']['android_button']
                    else:
                        pushed='long_pushed'
                        if 'KEY_VOLUMEUP' in str(categorize(event)) :
                            run_command = button['command']['ios_button_long']
                        elif 'KEY_ENTER' in str(categorize(event)):
                            run_command = button['command']['android_button_long']
                    logger.info(f"[{button['name']}] [RUN] button={pushed} command={run_command}")
                    try:
                        subprocess.run(run_command,shell=True)
                    except:
                        logger.error(f"[{button['name']}] run failed. command=  {run_command}")
    except KeyboardInterrupt:
        logger.info("KeyBoardInterrupt. program exit.")
        sys.exit()
    sys.exit() 

def find_connection(interface, changed, invalidated, path):
    iface = interface[interface.rfind(".") + 1:]
    logger.debug("iface={} path={}".format(iface,path))
    path2 = path.replace('_',':')
    for name, value in changed.items():
        val = str(value)
        logger.debug(f"{iface} PropertyChanged [{path}] {name} = {val}")

        for button in settings.button_setting:
            button_name = button['name']
            button_mac = button['mac']
            button_command = button['command']
            if button_mac in path2 and name == "Connected" and val == "1":
                logger.info(f"[{button_name}] Bluetooth Connected. [RUN] {button_command['connected']}")
                try:
                    subprocess.run(button_command['connected'],shell=True)
                except:
                    logger.error(f"[{button['name']}] run failed. command= {run_command}")
            elif button_mac in path2 and name == "Connected" and val == "0":
                logger.info(f"[{button_name}] Bluetooth disconnected.")

if __name__ == '__main__':

    prog_name = os.path.splitext(os.path.basename(__file__))[0]
    current_dir = os.path.dirname(__file__)

    # Logger setting
    logger = getLogger(__name__)
    
    # フォーマット
    log_format = Formatter("%(asctime)s [%(levelname)8s] %(funcName)s %(message)s")
    # レベル
    logger.setLevel(DEBUG)

    # 標準出力へのハンドラ
    stdout_handler = StreamHandler(sys.stdout)
    stdout_handler.setFormatter(log_format)
    stdout_handler.setLevel(settings.log['log_level']['stdout'])
    logger.addHandler(stdout_handler)

    # ログファイルへのハンドラ
    if (settings.log['log_file_output']):
        file_handler = FileHandler(current_dir+"/log/"+prog_name+"_"+datetime.now().strftime("%Y%m%d")+".log")
        file_handler.setFormatter(log_format)
        file_handler.setLevel(settings.log['log_level']['file'])
        logger.addHandler(file_handler)

    main()

