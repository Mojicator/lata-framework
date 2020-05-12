import json
import time
import os

from auida import AndroidDevice
from escribano import Log
import utils

DATA_TEST_FILE = 'data-test.json'
DELAY = 8

_error_handler = []

if __name__ == '__main__':
    try:
        test_path = os.path.join(os.getcwd(), DATA_TEST_FILE)
        if not os.path.exists(test_path):
            print("Test data file not found")
        else:
            android = AndroidDevice()
            android.select_device()
            log = Log(utils.get_version())
            log.start_test_log()
            with open('data-test.json') as json_file:
                data = json.load(json_file)
                # adb shell
                for wifi in data['wifies']:
                    android.adb_wifi_test(wifi)
                time.sleep(1)
                for phone in data['phones']:
                    android.adb_calling_test(phone, DELAY)
                # uiautomator
                time.sleep(1)
                for wifi in data['wifies']:
                    android.uia_settings_wifi_test(wifi)
                time.sleep(1)
                for wifi in data['wifies']:
                    android.uia_quick_wifi_test(wifi)
                time.sleep(1)
                for phone in data['phones']:
                    android.uia_calling_test(phone, DELAY)
                    
                android.uia_calculator_test(data['operations'])
            log.end_test_log()
    except Exception as e:
        _error_handler.append(e)
    finally:
        for error in _error_handler:
            print(error)