from auida import AndroidDevice
from log_record import Log
import time

DELAY = 2

def is_valid_number(number):
    """
    Verify the number given if it is correct for realise a call
    :param number: string Number to call given by the user
    :return: boolean True if is valid number or False otherwise
    """
    if number[0] == '+' or number[0] == '*':
        return number[1:].isdigit()
    return number.isdigit()

if __name__ == '__main__':
    android = AndroidDevice()
    android.select_device()
    log = Log()
    while True:
        print('Call a number\n' +
              '\t 1) by adb shell\n' +
              '\t 2) by uiautomator\n' +
              'Turn ON Wifi\n' +
              '\t 3) by adb shell\n' +
              '\t 4) by uiautomator\n' +
              'Turn OFF Wifi\n' +
              '\t 5) by adb shell\n' +
              '\t 6) by uiautomator\n' +
              '7) Exit')
        option = input('Select an operation: ')
        if option.isdigit():
            option = int(option)
            if option == 1:
                number = input('Enter the number to call: ')
                if is_valid_number(number):
                    android.adb_calling_test(number, DELAY)
            if option == 2:
                number = input('Enter the number to call: ')
                if is_valid_number(number):
                    android.uia_calling_test(number, DELAY)
            if option == 3:
                android.adb_wifi_test('ON')
            if option == 4:
                # android.settings_wifi_test('ON')
                android.uia_quick_wifi_test('ON')
            if option == 5:
                android.adb_wifi_test('OFF')
            if option == 6:
                # android.settings_wifi_test('OFF')
                android.uia_quick_wifi_test('OFF')
            if option == 7:
                break
            if option < 0 or option > 7:
                print('{0} is not a valid number'.format(option))
        else:
            print('{0} is not a valid number'.format(option))

