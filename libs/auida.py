from subprocess import check_call, check_output
from uiautomator import Device
import time
import json

from libs.escribano import escribano
import libs.utils as utils

NO_CONNECTED = 'Device not connected'
NO_SELECTED = 'No devices selected'

# WiFi status
DISCONNECTED = 'DISCONNECTED/DISCONNECTED'
CONNECTED = 'CONNECTED/CONNECTED'
UNKNOWN = 'UNKNOWN/IDLE'

# Calculator
CAL_DIVIDE_BY_ZERO = "Can't divide by 0"

class AndroidDevice(object):

    def __init__(self):
        self.device = None
        self.d = None
        self.sdk = 25
        self.btn_elements = {}

    # @escribano
    # def get_sdk(self):
    #     return { "sdk": self.sdk }

    def load_btn_elements_by_country(self):
        """
        """
        country_key = check_output(['adb', '-s', self.device, 'shell', 'getprop', 'gsm.operator.iso-country']).decode('utf-8')[:-1]
        print(country_key)
        if '\r' in country_key:
            country_key = country_key.replace('\r', '')
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
                self.get_api_level()
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

    def get_api_level(self):
        output = check_output(['adb', '-s', self.device, 'shell', 'getprop', 'ro.build.version.sdk']).decode('utf-8')[:-1]
        if '\r' in output:
            output = output.replace('\r', '')
        self.sdk = int(output)

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
        check_call(['adb', '-s', self.device, 'shell', 'input', 'keyevent 6'])

    def get_current_call_state(self):
        # 0: no hay nada | 1: sonando | 2: llamando
        output = check_output(['adb', '-s', self.device, 'shell', 'dumpsys', 'telephony.registry', '|', 'grep', 'mCallState'])
        line = output.split()[0].decode('utf-8')
        return int(line[-1])

    def get_current_wifi_state(self):
        output = check_output(['adb', '-s', self.device, 'shell', 'dumpsys', 'wifi', '|', 'grep', 'mNetworkInfo']).decode('utf-8')
        state = output[output.find('state'):output.find('reason')]
        return state.split()[1][:-1]

    def adb_open_settings(self):
        """
        Open the settings menu by adb shel command
        """
        check_call(['adb', '-s', self.device, 'shell', 'am', 'start', '-a', 'android.settings.SETTINGS'])

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
        time.sleep(2)
        _call = self.get_current_call_state()
        time.sleep(delay)
        self.hang_up()
        time.sleep(1)
        _hang_up = self.get_current_call_state()
        return {
            'sdk': self.sdk,
            'res': self.verify_call_process(_call, _hang_up)
        }

    @escribano
    def adb_wifi_test(self, value):
        """
        By the state given, turn on or turn off the wifi using adb shell command
        :param value: string It is the state to turn ON/OFF
        """
        if value == 0:
            self.turn_off_wifi_test()
            time.sleep(5)
            return {
                'sdk': self.sdk,
                'res': self.wifi_have_to_be(DISCONNECTED)
            }
        elif value == 1:
            self.turn_on_wifi_test()
            time.sleep(5)
            return {
                'sdk': self.sdk,
                'res': self.wifi_have_to_be(CONNECTED)
            }

    def find_by_image_button(self, text):
        _device = self.d(descriptionMatches='{0}'.format(text), className='android.widget.ImageButton')
        return _device

    def find_by_text_view(self, text):
        return self.d(text='{0}'.format(text), className='android.widget.TextView')

    def find_by_image_view(self, text):
        return self.d(descriptionContains='{0}'.format(text), className='android.widget.ImageView')

    def find_by_frame_layout(self, text):
        _device = self.d(descriptionContains='{0}'.format(text), className='android.widget.FrameLayout')
        return _device

    def find_by_switch(self, text):
        return self.d(descriptionContains='{0}'.format(text), className='android.widget.Switch')

    def find_by_switch_text(self, text):
        return self.d(text='{0}'.format(text), className='android.widget.Switch')

    def find_by_text_button(self, text):
        return self.d(text='{0}'.format(text), className='android.widget.Button')

    def find_by_desc_button(self, text):
        return self.d(descriptionMatches='{0}'.format(text), className='android.widget.Button')

    def get_wifi_switch_bar(self):
        return self.d(resourceId='com.android.settings:id/switch_bar', className='android.widget.Switch')

    def get_wifi_switch_widget(self):
        return self.d(resourceId='com.android.settings:id/switchWidget', className='android.widget.Switch')

    def get_wifi_toggle_bar(self):
        return self.d(resourceId='android:id/toggle', className='android.widget.Switch')

    def get_wifi_quick_btn(self, text):
        return self.d(descriptionContains='{0}'.format(text), className='android.widget.Button')

    def get_wifi_quick_switch(self, text):
        return self.d(descriptionContains='{0}'.format(text), className='android.widget.Switch')

    def find_by_index_class(self, index_e, class_name):
        return self.d(index=index_e, className='android.widget.{0}'.format(class_name))

    def get_formula_display(self):
        return self.d(textMatches=r'^[-]*[0-9]*\.?[0-9]*$', className='android.widget.TextView')

    def get_display_result(self):
        if self.sdk > 25:
            return self.d(resourceId='com.google.android.calculator:id/result', className='android.widget.TextView')
        else:
            return self.d(resourceId='com.android.calculator2:id/result', className='android.widget.TextView')
    
    def type_number(self, number):
        """
        This function iterates through the number given and click each digit
        :param number: string It is the number to call
        """
        for digit in number:
            if digit == '+':
                _btn_bounds = self.find_by_frame_layout('0').info['bounds']
                self.d.swipe(_btn_bounds['left'], _btn_bounds['top'],
                             _btn_bounds['right'], _btn_bounds['bottom'], steps=30)
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
        self.open_all_applications_menu()
        time.sleep(2)
        self.find_by_text_view(self.btn_elements['phone']).click()
        time.sleep(3)
        if self.sdk > 25:
            self.find_by_image_button(self.btn_elements['key-pad'][0]).click()
        else:
            self.find_by_image_button(self.btn_elements['key-pad'][1]).click()
        time.sleep(1)
        self.type_number(number)
        self.find_by_image_button(self.btn_elements['dial']).click()
        time.sleep(delay)
        _call = self.get_current_call_state()
        time.sleep(1)
        if self.sdk > 25:
            self.find_by_image_button(self.btn_elements['end-call'][0]).click()
        else:
            self.find_by_image_button(self.btn_elements['end-call'][1]).click()
        time.sleep(1)
        _hang_up = self.get_current_call_state()
        time.sleep(1)
        self.d.press.home()
        time.sleep(1)
        return {
            'sdk': self.sdk,
            'res': self.verify_call_process(_call, _hang_up)
        }

    def quick_turn_on_wifi(self):
        """
        Open the quick settings menu to turn on the wifi.
        """
        if self.sdk > 25:
            _wifi_btn = self.get_wifi_quick_switch('Wi-Fi,')
            if not _wifi_btn.checked:
                _wifi_btn.click()
        else:
            _wifi_btn = self.get_wifi_quick_btn('Wi-Fi')
            _wifi_btn.click()
            _wifi_switch_switch = self.get_wifi_toggle_bar()
            if not _wifi_switch_switch.checked:
                _wifi_switch_switch.click()
        time.sleep(2)
        
    def quick_turn_off_wifi(self):
        """
        Open the quick settings menu to turn off the wifi
        """
        if self.sdk > 25:
            _wifi_btn = self.get_wifi_quick_switch('Wi-Fi,')
            if _wifi_btn.checked:
                _wifi_btn.click()
        else:
            _wifi_btn = self.get_wifi_quick_btn('Wi-Fi')
            _wifi_btn.click()
            _wifi_switch_switch = self.get_wifi_toggle_bar()
            if _wifi_switch_switch.checked:
                _wifi_switch_switch.click()
        time.sleep(2)

    @escribano
    def uia_quick_wifi_test(self, value):
        """
        By the state given, open the quick settings menu and turn on or turn off the
        wifi using uiautomator
        :param on_off: string It is the state to turn
        """
        self.d.press.home()
        self.d.open.quick_settings()
        time.sleep(10)
        if value == 0:
            self.quick_turn_off_wifi()
            time.sleep(4)
            return {
                'sdk': self.sdk,
                'res': self.wifi_have_to_be(DISCONNECTED)
            }
        elif value == 1:
            self.quick_turn_on_wifi()
            time.sleep(8)
            return {
                'sdk': self.sdk,
                'res': self.wifi_have_to_be(CONNECTED)
            }

    def setting_turn_on_wifi(self):
        """
        Look for the wifi button and check if it is enable. If
        it is already on, it won't do anything.
        """
        if self.sdk > 25:
            _wifi_switch = self.find_by_switch('Wi-Fi')
        else:
            _wifi_switch = self.get_wifi_switch_bar()
        if not _wifi_switch.checked:
            _wifi_switch.click()
        
    def setting_turn_off_wifi(self):
        """
        Look for the wifi button and check if it is enable. If
        it is already off, it won't do anything.
        """
        if self.sdk > 25:
            _wifi_switch = self.find_by_switch('Wi-Fi')
        else:
            _wifi_switch = self.get_wifi_switch_bar()
        if _wifi_switch.checked:
            _wifi_switch.click()
    
    @escribano
    def uia_settings_wifi_test(self, value):
        """
        By the state given, open the settings menu and turn on or turn off the wifi
        using uiautomator
        :param on_off: string It is the state to turn
        """
        self.d.press.home()
        time.sleep(1)
        self.adb_open_settings()
        time.sleep(2)
        if self.sdk > 25:
            self.find_by_text_view(self.btn_elements['wifi'][1]).click()
        else:
            self.find_by_text_view(self.btn_elements['wifi'][1]).click()
        time.sleep(2)
        if value == 0:
            self.setting_turn_off_wifi()
            time.sleep(4)
            return {
                'sdk': self.sdk,
                'res': self.wifi_have_to_be(DISCONNECTED)
            }
        elif value == 1:
            self.setting_turn_on_wifi()
            time.sleep(8)
            return {
                'sdk': self.sdk,
                'res': self.wifi_have_to_be(CONNECTED)
            }

    def open_all_applications_menu(self):
        if self.sdk > 25:
            # print(28)
            self.d.swipe(500, 800, 500, 100, steps=10)
        else:
            # print(25)
            self.d.swipe(360, 980, 360, 100, steps=10)
            # _up_button = self.find_by_image_view('Apps list')
            # _up_button.click()

    def enter_operation(self, operation):
        for character in operation:
            if character == '+':
                self.find_by_desc_button(self.btn_elements['operations'][0]).click()
            elif character == '-':
                self.find_by_desc_button(self.btn_elements['operations'][1]).click()
            elif character == '/':
                self.find_by_desc_button(self.btn_elements['operations'][3]).click()
            elif character == '*':
                self.find_by_desc_button(self.btn_elements['operations'][2]).click()
            else:
                self.find_by_text_button(character).click()            

    def press_clear_btn(self):
        self.find_by_desc_button(self.btn_elements['operations'][5]).click()

    def press_del_btn(self):
        if self.sdk > 25:
            self.find_by_image_button(self.btn_elements['operations'][4]).click()
        else:
            self.find_by_desc_button(self.btn_elements['operations'][4]).click()

    def press_equal_btn(self):
        self.find_by_text_button('=').click()

    def verify_result_operation(self, expected_value, actual_value):
        if expected_value == actual_value:
            print(utils.TGREEN + '.' + utils.TNOR)
            return True
        else:
            print(utils.TRED + 'F' + utils.TNOR)
            return Exception('UIAUTOMATOR OPERATION ERROR :: Expected {0} but got {1}'
                             .format(expected_value, actual_value))

    @escribano
    def single_operation(self, operation_to_do, expected_result):
        self.enter_operation(operation_to_do)
        self.press_equal_btn()
        actual_result = self.get_display_result().info['text']
        if isinstance(expected_result, list):
            if actual_result in expected_result:
                return {
                    'sdk': self.sdk,
                    'res': self.verify_result_operation(expected_result[expected_result.index(actual_result)], actual_result)
                }
        else:
            return {
                'sdk': self.sdk,
                'res': self.verify_result_operation(expected_result, utils.clean_string_negative_values(actual_result))
            }

    def uia_calculator_test(self, operations_to_do):
        self.d.press.home()
        self.open_all_applications_menu()
        time.sleep(3)
        self.find_by_text_view(self.btn_elements['calculator']).click()
        time.sleep(1)
        for operation in operations_to_do:
            self.single_operation(operation[0], operation[1])
            time.sleep(1)
            if isinstance(operation[1], list):
                _del_count = 0
                while _del_count < len(operation[0]):
                    self.press_del_btn()
                    _del_count += 1
            else:
                self.press_clear_btn()
            time.sleep(1)
    