from datetime import datetime
import os

DIR_NAME = 'output_test'
FILE_NAME = 'log.txt'

class Log:
    def __init__(self):
        self.serial = ''
        self.number = ''
        self.wifi = ''
        self.test_start = ''
        self.test_end = ''
        self.path_name = os.getcwd()

    def set_serial(self, device):
        """
        Handle the device's serial ID.
        :params device: string Serial ID
        """
        self.serial = device

    def set_wifi_status(self, status):
        """
        Handle the wifi status
        :params status: string Wifi status ON/OFF
        """
        self.wifi_status = status
        print('WIFI: {0}'.format(self.wifi_status))
    
    def set_call(self, serial, number):
        """
        Handle the device's serial and the number to call
        :param serial: string Serial ID
        :param number: string Number to call
        """
        self.serial = serial
        self.number = number
        print('DEVICE: {0} CALLING {1}'.format(self.serial, self.number))

    def set_event(self, event):
        """
        Handle the event given with its datetime
        :param event: string START/END
        """
        if event == 'START':
            self.test_start = datetime.now()
            print('START at {0}'.format(self.test_start))
        elif event == 'END':
            self.test_end = datetime.now()
            print('END at {0}'.format(self.test_end))
        else:
            pass

    def add_log(self, action):
        """
        By the action given, wirte on a file the test status with all the information.
        :param action: string CALL/WIFI
        """
        path = os.path.join(self.path_name, DIR_NAME)
        if not os.path.exists(path):
            os.mkdir(path)
        with open(os.path.join(path, FILE_NAME), mode='a') as file:
            if action == 'CALL':
                file.write('DEVICE: {0} CALLED {1}\nSTART at {2} -> END at {3}\n-\n'
                .format(self.serial, self.number, self.test_start, self.test_end))
            elif action == 'WIFI':
                file.write('DEVICE: {0} WIFI: {1}\nSTART at {2} -> END at {3}\n-\n'
                .format(self.serial, self.wifi_status, self.test_start, self.test_end))
