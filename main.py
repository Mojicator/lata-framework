import json
import time
import os

from subprocess import check_call, check_output

from auida import AndroidDevice
from log_record import Log

VERSION = 2.0

DATA_TEST_FILE = 'data-test.json'
DELAY = 8

if __name__ == '__main__':
    test_path = os.path.join(os.getcwd(), DATA_TEST_FILE)
    if not os.path.exists(test_path):
        print("Test data file not found")
    else:
        android = AndroidDevice()
        android.select_device()
        print(android.device)
        check_call(['adb', '-s', android.device, 'shell', 'am', 'start',
                        '-a', 'android.intent.action.CALL', '-d', 'tel:{0}'.format('911')])
        # log = Log()
        # android.dial_number('911')
        time.sleep(3)
        # with open('data-test.json') as json_file:
        #     data = json.load(json_file)
        #     for phone in data['phones']:
        #         # android.adb_calling_test(phone, DELAY)
        #         time.sleep(10)

        #     android.initial_state()

            # for operation in data['operations']:
            #     print(operation[0])
