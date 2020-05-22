import json
import time
import argparse
import threading
import os

from libs.openstf import Overseer
from libs.auida import AndroidDevice
from libs.escribano import Log
import libs.utils as utils

DATA_TEST_FILE = 'data-test.json'
DELAY = 6

_error_handler = []

def execute_testing(device):
    android = AndroidDevice()
    android.select_device(device)
    log = Log(utils.get_version(), android.sdk)
    log.start_test_log()
    with open('data-test.json') as json_file:
        data = json.load(json_file)
        time.sleep(1)
        for wifi in data['wifies']:
            android.uia_settings_wifi_test(wifi)
        time.sleep(1)
        for wifi in data['wifies']:
                android.uia_quick_wifi_test(wifi)
        time.sleep(1)
        android.d.press.home()
        for phone in data['phones']:
            android.uia_calling_test(phone, DELAY)
        time.sleep(1)
        android.uia_calculator_test(data['operations'])
    log.end_test_log()

def single_device_execution(index):
    overseer.use_device(index)
    time.sleep(1)
    overseer.get_adb_debug_connection(index)
    overseer.connect_adb_device(index)
    execute_testing(index + 1)
    overseer.disconnect_adb_device(index)
    overseer.stop_using_device(index)
    time.sleep(5)

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser('LATA Framework')
        parser.add_argument('local', nargs='?', help='Execute on local machine')
        parser.add_argument('--stf', nargs=1, help='Connect to the STF server')
        args = parser.parse_args()
        test_path = os.path.join(os.getcwd(), DATA_TEST_FILE)
        if not os.path.exists(test_path):
            print("Test data file not found")
        else:
            if args.local:
                execute_testing(1)
            elif args.stf:
                overseer = Overseer(args.stf[0])
                overseer.get_all_connected_devices()
                no_devices = len(overseer.devices)
                threads = list()
                for i in range(no_devices):
                    t = threading.Thread(target=single_device_execution, args=(i,))
                    threads.append(t)
                    t.start()
    except Exception as e:
        _error_handler.append(e)
    finally:
        for error in _error_handler:
            print(error)