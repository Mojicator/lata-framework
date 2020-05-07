from subprocess import check_call, check_output
from uiautomator import Device
import time

from escribano import escribano

NO_CONNECTED = 'Device not connected'
NO_SELECTED = 'No devices selected'

class AndroidDevice(object):
    message_error = 'aiuda::AndroidDevice#{0} Error: {1}'

    def __init__(self):
        self.device = None
        self.d = None

    def select_device(self, device = 1):
        """
        Verify and return the serial device available. By default return
        the first device found.
        :param device: string This is the number of the selected device
        :return: string Returns the serial device
        """
        list_devices = check_list()
        if list_devices:
            if device <= 0 or device > len(list_devices):
                print(NO_SELECTED)
                exit()
            else:
                self.device = list_devices[device - 1].split()[0].decode('utf-8')
                self.d = Device(self.device)
                print('>>>> Device selected: ' + self.device + ' <<<<')
                return self.device
        else:
            print(NO_CONNECTED)
            exit()

    def dial_number(self, number):
        """
        Call to the specified number by adb shell command
        :param number: string It is the number to call
        """
        if self.device:
            # TODO: validar si el numero es valido
            check_call(['adb', '-s', self.device, 'shell', 'am', 'start',
                        '-a', 'android.intent.action.CALL', '-d', 'tel:{0}'.format(number)])
        else:
            raise Exception(self.message_error.format('dial_number', NO_CONNECTED))

    def call_state(self):
        # adb shell dumpsys telephony.registry | grep mCallState
        # TODO: verificar el estado de la llamada | 0: no hay nada | 1: sonando | 2: llamando
        pass
        
    def hang_up(self):
        """
        Hang up or cancel the calling if there is one in progress
        """
        if self.device:
            check_call(['adb', 'shell', 'input', 'keyevent 6'])
        else:
            raise Exception(self.message_error.format('hang_up', NO_CONNECTED))

    def adb_open_settings(self):
        """
        Open the settings menu by adb shel command
        """
        check_call(['adb', 'shell', 'am', 'start', '-a', 'android.settings.SETTINGS'])

    def turn_on_wifi(self):
        """
        Turn on the wifi by adb shell command
        """
        check_call(['adb', '-s', self.device, 'shell', 'svc wifi enable'])

    def turn_off_wifi(self):
        """
        Turn off the wifi by adb shell command
        """
        check_call(['adb', '-s', self.device, 'shell', 'svc wifi disable'])

    @escribano
    def adb_calling_test(self, number, delay = 5):
        """
        Call to the number given and hangs up after the time specified
        :param number: string It is the number to call
        :param delay: int It is the time between the call event and hang up event
        """
        self.dial_number(number)
        time.sleep(delay)
        self.hang_up()
        # TODO: validacion de status
        return True

    def adb_wifi_test(self, on_off):
        """
        By the state given, turn on or turn off the wifi using adb shell command
        :param on_off: string It is the state to turn ON/OFF
        """
        if on_off == 'ON':
            self.turn_on_wifi()
        elif on_off == 'OFF':
            self.turn_off_wifi()

    def uiaviewer_generator(self, name_file):
        """
        Take a screenshot fo the current device's screen in png and uix format
        and save them on project root.
        """
        self.d.screenshot('{0}.png'.format(name_file))
        self.d.dump('{0}.uix'.format(name_file))

    def click_espanglish_button(self, matcher, spanish, english, class_name, matcher_aux = None):
        """
        This function looks for the element specified by a UIMatcher and className and click it.
        If 'matcher_aux' is specified, the function will look for again with UIMatcher specified
        :param matcher: string First UIMatcher to look for
        :param spanish: string Label of the element translated to Spanish
        :param english: string Label of the element translated to English
        :param class_name: string android.widget name
        :param matcher_aux: string Secondary UIMatcher to look for
        """
        if matcher == 'text':
            d_aux = self.d(text='{0}'.format(spanish), className='android.widget.{0}'.format(class_name))
            if d_aux.exists:
                d_aux.click()
            else:
                self.d(text='{0}'.format(english), className='android.widget.{0}'.format(class_name)).click()
        elif matcher == 'descriptionMatches':
            d_aux = self.d(descriptionMatches='{0}'.format(spanish), className='android.widget.{0}'.format(class_name))
            if d_aux.exists:
                d_aux.click()
            else:
                if matcher_aux:
                    self.click_espanglish_button('text', spanish, english, 'TextView')
                else:
                    self.d(descriptionMatches='{0}'.format(english), className='android.widget.{0}'.format(class_name)).click()
        elif matcher == 'descriptionContains':
            d_aux = self.d(descriptionContains='{0}'.format(spanish), className='android.widget.{0}'.format(class_name))
            if d_aux.exists:
                d_aux.click()
            else:
                self.d(descriptionContains='{0}'.format(english), className='android.widget.{0}'.format(class_name)).click()
        elif matcher == 'index':
            d_aux = self.d(index='{0}'.format(spanish), className='android.widget.{0}'.format(class_name))
            if d_aux.exists:
                d_aux.click()
            else:
                self.d(index='{0}'.format(english), className='android.widget.{0}'.format(class_name)).click()

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
            # self.d(text='{0}'.format(digit), className='android.widget.TextView').click()
            self.d(descriptionContains='{0}'.format(digit), className='android.widget.FrameLayout').click()

    def uia_calling_test(self, number, delay = 5):
        """
        This function sets the device on the home screen and calls the number given, after a certain time
        hangs up.
        :param number: string It is the number to call
        :param delay: int Time between call event and hang up event
        """
        self.initial_state()
        self.click_espanglish_button('descriptionMatches', 'Teléfono', 'Phone', 'ImageView', 'text')
        time.sleep(3)
        self.click_espanglish_button('descriptionMatches', 'teclado', 'key pad', 'ImageButton')
        self.type_number(number)
        self.click_espanglish_button('descriptionMatches', 'marcar', 'dial', 'ImageButton')
        time.sleep(delay)
        self.click_espanglish_button('descriptionMatches', 'Finalizar llamada', 'End call', 'ImageButton')

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
    
    def settings_wifi_test(self, on_off):
        """
        By the state given, open the settings menu and turn on or turn off the wifi
        using uiautomator
        :param on_off: string It is the state to turn
        """
        self.adb_open_settings()
        time.sleep(3)
        self.click_espanglish_button('text', 'Wi-Fi', 'Network & internet', 'TextView')
        time.sleep(3)
        self.uiaviewer_generator('redminote_9_wifi_settings')
        if on_off == 'ON':
            self.setting_turn_on_wifi()
        elif on_off == 'OFF':
            self.setting_turn_off_wifi()
        time.sleep(3)
        self.d.press.home()
    
def check_list():
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
        
    