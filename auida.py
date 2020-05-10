from subprocess import check_call, check_output
from uiautomator import Device
import time
import json

from escribano import escribano
import utils

dictionary_key = { 'phone': 0, 'key-pad': 1, 'dial': 2, 'end-call': 3 }

NO_CONNECTED = 'Device not connected'
NO_SELECTED = 'No devices selected'

# WiFi status
DISCONNECTED = 'DISCONNECTED/DISCONNECTED'
CONNECTED = 'CONNECTED/CONNECTED'
UNKNOWN = 'UNKNOWN/IDLE'

class AndroidDevice(object):
    message_error = 'aiuda::AndroidDevice#{0} Error: {1}'

    def __init__(self):
        self.device = None
        self.d = None
        self.btn_elements = {}

    def load_btn_elements_by_country(self):
        country_key = check_output(['adb', 'shell', 'getprop', 'gsm.operator.iso-country']).decode('utf-8')[:-1]
        with open('dictionary.json') as json_file:
            data = json.load(json_file)
            self.btn_elements = data[country_key]


    def select_device(self, device = 1):
        """
        Verify and return the serial device available. By default return
        the first device found.
        :param device: string This is the number of the selected device
        :return: string Returns the serial device
        """
        list_devices = self.check_list()
        if list_devices:
            if device <= 0 or device > len(list_devices):
                print(NO_SELECTED)
                exit()
            else:
                self.device = list_devices[device - 1].split()[0].decode('utf-8')
                self.d = Device(self.device)
                print('>>>> Device selected: ' + self.device + ' <<<<')
                self.load_btn_elements_by_country()
                return self.device
        else:
            print(NO_CONNECTED)
            exit()

    def check_list(self):
        """
        Using adb shell command, checks if there are devices connected and
        retruns them on a list
        :return: array List of available devices
        """
        output = check_output(['adb', 'devices'])
        lines = output.splitlines()[1:-1]
        if not lines or lines[0] == b'':
            return None
        else:
            return lines

    def dial_number(self, number):
        """
        Call to the specified number by adb shell command
        :param number: string It is the number to call
        """
        check_call(['adb', '-s', self.device, 'shell', 'am', 'start',
                    '-a', 'android.intent.action.CALL', '-d', 'tel:{0}'.format(number)])

    def hang_up(self):
        """
        Hang up or cancel the calling if there is one in progress
        """
        check_call(['adb', 'shell', 'input', 'keyevent 6'])

    def get_current_call_state(self):
        # 0: no hay nada | 1: sonando | 2: llamando
        output = check_output(['adb', 'shell', 'dumpsys', 'telephony.registry', '|', 'grep', 'mCallState'])
        line = output.split()[0].decode('utf-8')
        return int(line[-1])

    def get_current_wifi_state(self):
        output = check_output(['adb', 'shell', 'dumpsys', 'wifi', '|', 'grep', 'mNetworkInfo']).decode('utf-8')
        state = output[output.find('state'):output.find('reason')]
        return state.split()[1][:-1]

    def adb_open_settings(self):
        """
        Open the settings menu by adb shel command
        """
        check_call(['adb', 'shell', 'am', 'start', '-a', 'android.settings.SETTINGS'])

    def turn_on_wifi_test(self):
        """
        Turn on the wifi by adb shell command
        """
        check_call(['adb', '-s', self.device, 'shell', 'svc wifi enable'])

    def turn_off_wifi_test(self):
        """
        Turn off the wifi by adb shell command
        """
        check_call(['adb', '-s', self.device, 'shell', 'svc wifi disable'])

    def verify_call_process(self, calling, hang_up):
        if calling == 2 and hang_up == 0:
            # hang up correctly
            print(utils.TGREEN + '.' + utils.TNOR)
            return True
        elif calling == 0 and hang_up == 2:
            # call out of time
            print(utils.TRED + 'F' + utils.TNOR)
            return Exception('ADB Call error :: Call started out of time')
        elif calling == 2 and hang_up == 2:
            # still calling
            print(utils.TRED + 'F' + utils.TNOR)
            return Exception('ADB Call error :: Should hang up but still was calling')
        elif calling == 0 and hang_up == 0:
            # did not call
            print(utils.TRED + 'F' + utils.TNOR)
            return Exception('ADB Call error :: Should call but did not start')

    def wifi_have_to_be(self, expected_value):
        real_value = self.get_current_wifi_state()
        if expected_value == real_value:
            print(utils.TGREEN + '.' + utils.TNOR)
            return True
        else:
            print(utils.TRED + 'F' + utils.TNOR)
            return Exception('ADB WiFi error state :: Expected {0} but got {1}'.format(expected_value, real_value))

    @escribano
    def adb_calling_test(self, number, delay = 5):
        """
        Call to the number given and hangs up after the time specified
        :param number: string It is the number to call
        :param delay: int It is the time between the call event and hang up event
        """
        self.dial_number(number)
        time.sleep(1)
        _call = self.get_current_call_state()
        time.sleep(delay)
        self.hang_up()
        time.sleep(1)
        _hang_up = self.get_current_call_state()
        return self.verify_call_process(_call, _hang_up)

    @escribano
    def adb_wifi_test(self, value):
        """
        By the state given, turn on or turn off the wifi using adb shell command
        :param value: string It is the state to turn ON/OFF
        """
        if value == 0:
            self.turn_off_wifi_test()
            time.sleep(5)
            return self.wifi_have_to_be(DISCONNECTED)
        elif value == 1:
            self.turn_on_wifi_test()
            time.sleep(5)
            return self.wifi_have_to_be(CONNECTED)

    def uiaviewer_generator(self, name_file):
        """
        Take a screenshot fo the current device's screen in png and uix format
        and save them on project root.
        """
        self.d.screenshot('{0}.png'.format(name_file))
        self.d.dump('{0}.uix'.format(name_file))


    def find_by_image_button(self, text):
        _device = self.d(descriptionMatches='{0}'.format(text), className='android.widget.ImageButton')
        return _device

    def find_by_text_view(self, text):
        _device = self.d(text='{0}'.format(text), className='android.widget.TextView')
        return _device

    def find_by_image_view(self, text):
        pass

    def find_by_frame_layout(self, text):
        _device = self.d(descriptionContains='{0}'.format(text), className='android.widget.FrameLayout')
        return _device

    def initial_state(self):
        """
        This function sets the device on the home screen
        """
        self.d.screen.on()
        self.d.press.home()
    
    def type_number(self, number):
        """
        This function iterates through the number given and click each digit
        :param number: string It is the number to call
        """
        for digit in number:
            if digit == '+':
                _btn_bounds = self.find_by_frame_layout('0').info['bounds']
                self.d.swipe(_btn_bounds['left'], _btn_bounds['top'],
                             _btn_bounds['right'], _btn_bounds['bottom'], steps=20)
            else:
                self.find_by_frame_layout(digit).click()

    @escribano
    def uia_calling_test(self, number, delay = 5):
        """
        This function sets the device on the home screen and calls the number given, after a certain time
        hangs up.
        :param number: string It is the number to call
        :param delay: int Time between call event and hang up event
        """
        self.d.press.home()
        self.find_by_text_view(self.btn_elements['phone']).click()
        time.sleep(3)
        self.find_by_image_button(self.btn_elements['key-pad']).click()
        time.sleep(1)
        self.type_number(number)
        self.find_by_image_button(self.btn_elements['dial']).click()
        time.sleep(delay)
        _call = self.get_current_call_state()
        time.sleep(1)
        self.find_by_image_button(self.btn_elements['end-call']).click()
        time.sleep(1)
        _hang_up = self.get_current_call_state()
        time.sleep(1)
        self.d.press.home()
        time.sleep(1)
        return self.verify_call_process(_call, _hang_up)

    def quick_turn_on_wifi(self):
        """
        Open the quick settings menu to turn on the wifi.
        """
        self.d.open.quick_settings()
        time.sleep(3)
        status = self.d(index=1, className='android.widget.Switch').checked
        if not status:
            self.d(index=1, className='android.widget.Switch').click()
        else:
            print('Wifi is already turned on')
        self.d.press.home()
        
    def quick_turn_off_wifi(self):
        """
        Open the quick settings menu to turn off the wifi
        """
        self.d.open.quick_settings()
        time.sleep(3)
        status = self.d(index=1, className='android.widget.Switch').checked
        if status:
            self.d(index=1, className='android.widget.Switch').click()
        else:
            print('Wifi is already turned off')
        self.d.press.home()

    def uia_quick_wifi_test(self, on_off):
        """
        By the state given, open the quick settings menu and turn on or turn off the
        wifi using uiautomator
        :param on_off: string It is the state to turn
        """
        print('->')
        self.d.open.quick_settings()
        time.sleep(3)
        if on_off == 'ON':
            self.quick_turn_on_wifi()
        elif on_off == 'OFF':
            self.quick_turn_off_wifi()
        time.sleep(3)
        self.d.press.home()

    def setting_turn_on_wifi(self):
        """
        Look for the wifi button and check if it is enable. If
        it is already on, it won't do anything.
        """
        _wifi = self.d(text='Wi-Fi', className='android.widget.TextView')
        if not _wifi.enabled:
            # self.d(text='Wi-Fi', className='android.widget.TextView').click()
            self.d.click(472, 320)
        else:
            print('Wifi is already turned on')
        
    def setting_turn_off_wifi(self):
        """
        Look for the wifi button and check if it is enable. If
        it is already off, it won't do anything.
        """
        _wifi = self.d(text='Wi-Fi', className='android.widget.TextView')
        if _wifi.enabled:
            # self.d(text='{0}'.format(digit), className='android.widget.TextView').click()
            self.d.click(472, 320)
        else:
            print('Wifi is already turned off')
    
    # def settings_wifi_test(self, on_off):
    #     """
    #     By the state given, open the settings menu and turn on or turn off the wifi
    #     using uiautomator
    #     :param on_off: string It is the state to turn
    #     """
    #     self.adb_open_settings()
    #     time.sleep(3)
    #     self.click_espanglish_button('text', 'Wi-Fi', 'Network & internet', 'TextView')
    #     time.sleep(3)
    #     self.uiaviewer_generator('redminote_9_wifi_settings')
    #     if on_off == 'ON':
    #         self.setting_turn_on_wifi()
    #     elif on_off == 'OFF':
    #         self.setting_turn_off_wifi()
    #     time.sleep(3)
    #     self.d.press.home()
    