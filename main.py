import json
import time
import os

# from auida import AndroidDevice
from escribano import Log

VERSION = 2.0

DATA_TEST_FILE = 'data-test.json'
DELAY = 8

if __name__ == '__main__':
    test_path = os.path.join(os.getcwd(), DATA_TEST_FILE)
    if not os.path.exists(test_path):
        print("Test data file not found")
    else:
        # android = AndroidDevice()
        # android.select_device()
        log = Log()
        log.start_test_log()
        time.sleep(5)
        log.end_test_log()
        # with open('data-test.json') as json_file:
        #     data = json.load(json_file)
        #     for phone in data['phones']:
        #         android.adb_calling_test(phone, DELAY)

            # for operation in data['operations']:
            #     print(operation[0])
