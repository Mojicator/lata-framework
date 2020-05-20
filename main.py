import json
import time
import argparse
import os

from openstf import Overseer
from auida import AndroidDevice
from escribano import Log
import utils

DATA_TEST_FILE = 'data-test.json'
DELAY = 8

_error_handler = []

def execute_testing():
    android = AndroidDevice()
    android.select_device()
    print(android.btn_elements['wifi'][1])
    # log = Log(utils.get_version())
    # log.start_test_log()
    with open('data-test.json') as json_file:
        data = json.load(json_file)
        # adb shell
        # for wifi in data['wifies']:
        #     android.adb_wifi_test(wifi)
        # time.sleep(1)
        # for phone in data['phones']:
        #     android.adb_calling_test(phone, DELAY)
        # uiautomator
        time.sleep(1)
        for wifi in data['wifies']:
            android.uia_settings_wifi_test(wifi)
        time.sleep(1)
        # for wifi in data['wifies']:
        #     android.uia_quick_wifi_test(wifi)
        # time.sleep(1)
        # for phone in data['phones']:
        #     android.uia_calling_test(phone, DELAY)
            
    #     android.uia_calculator_test(data['operations'])
    # log.end_test_log()

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser('LATA Framework')
        parser.add_argument('local', nargs='?', help='Execute on local machine')
        parser.add_argument('--stf', nargs=1, help='Connect to the STF server')
        args = parser.parse_args()
        # print(args)
        test_path = os.path.join(os.getcwd(), DATA_TEST_FILE)
        if not os.path.exists(test_path):
            print("Test data file not found")
        else:
            if args.local:
                execute_testing()
            elif args.stf:
                overseer = Overseer()
                overseer.get_all_connected_devices()
                no_devices = len(overseer.devices)
                # print(no_devices)
                # i = 0
                for i in range(1):
                    overseer.use_device(i)
                    time.sleep(1)
                    overseer.connect_adb_device(i)
                    execute_testing()
                    # overseer.disconnect_adb_device(i)
                    # overseer.stop_using_device(i)
                    # time.sleep(5)
                    # i+=1
    except Exception as e:
        _error_handler.append(e)
    finally:
        for error in _error_handler:
            print(error)