import json
import time
import argparse
import os

from libs.openstf import Overseer
from libs.auida import AndroidDevice
from libs.escribano import Log
import libs.utils as utils
# import libs.openstf
# import libs.auida
# import libs.escribano
# import libs.utils

DATA_TEST_FILE = 'data-test.json'
DELAY = 8

_error_handler = []

def execute_testing():
    android = AndroidDevice()
    android.select_device()
    log = Log(utils.get_version())
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
        for phone in data['phones']:
            android.uia_calling_test(phone, DELAY)
        time.sleep(1)
        android.uia_calculator_test(data['operations'])
    log.end_test_log()

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
                execute_testing()
            elif args.stf:
                overseer = Overseer()
                overseer.get_all_connected_devices()
                no_devices = len(overseer.devices)
                for i in range(1):
                    overseer.use_device(i)
                    time.sleep(1)
                    overseer.connect_adb_device(i)
                    execute_testing()
                    overseer.disconnect_adb_device(i)
                    overseer.stop_using_device(i)
                    time.sleep(5)
    except Exception as e:
        _error_handler.append(e)
    finally:
        for error in _error_handler:
            print(error)