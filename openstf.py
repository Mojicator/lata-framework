import requests
from urllib.parse import urljoin
from subprocess import check_call, check_output

TOKEN = '27d177586c1d45d898e855b2af30c14b0a6cfacb35724451b8d1e51430756088'
STF_URL = 'http://192.168.0.4:7106'

class Overseer(object):
    def __init__(self):
        self.farm_ip = ''
        self.farm_port = ''
        self.devices = []

    def get_all_connected_devices(self):
        headers = {
            'Content-type': 'application/json',
            'Authorization': 'Bearer {}'.format(TOKEN)
        }
        api_call = '/api/v1/devices/'
        url = urljoin(STF_URL, api_call)
        res = requests.get(url, headers=headers).json()
        if not res['success']:
            raise Exception(res['description'])
        _devices = res['devices']
        for device in _devices:
            if device['present']:
                self.devices.append({
                    'serial': device['serial'],
                    'remoteConnectUrl': device['remoteConnectUrl']
                })

    def get_adb_debug_connection(self, index):
        headers = {
            'Content-type': 'application/json',
            'Authorization': 'Bearer {}'.format(TOKEN)
        }
        api_call = '/api/v1/user/devices/{0}'.format(self.devices[index]['serial'])
        url = urljoin(STF_URL, api_call)
        res = requests.get(url, headers=headers).json()
        if not res['success']:
            raise Exception(res['description'])
        self.devices[index]['remoteConnectUrl'] = res['device']['remoteConnectUrl']
        print('Using device: {0} | URL: {1}'.format(self.devices[index]['serial'], self.devices[index]['remoteConnectUrl']))

    def use_device(self, index):
        headers = {
            'Content-type': 'application/json',
            'Authorization': 'Bearer {}'.format(TOKEN)
        }
        data = '{{\"serial\": \"{0}\"}}'.format(self.devices[index]['serial'])
        api_call = '/api/v1/user/devices'
        url = urljoin(STF_URL, api_call)
        res = requests.post(url, data=data, headers=headers)
        calis = res.json()
        if not calis['success']:
            raise Exception(res['description'])
        self.get_adb_debug_connection(index)

    def stop_using_device(self, index):
        headers = {
            'Content-type': 'application/json',
            'Authorization': 'Bearer {}'.format(TOKEN)
        }
        api_call = '/api/v1/user/devices/{0}'.format(self.devices[index]['serial'])
        url = urljoin(STF_URL, api_call)
        res = requests.delete(url, headers=headers).json()
        if not res['success']:
            raise Exception(res['description'])
        self.devices[index]['remoteConnectUrl'] = None
        print('Stop using device: {}'.format(self.devices[index]['serial']))

    def connect_adb_device(self, index):
        _device = self.devices[index]['remoteConnectUrl']
        print('Connecting adb: {}'.format(_device))
        check_call(['adb', 'connect', _device])


    def disconnect_adb_device(self, index):
        _device = self.devices[index]['remoteConnectUrl']
        output = check_output(['adb', 'disconnect', _device]).decode('utf-8')
        if not 'disconnected' in output:
            raise Exception(output)
        print('Disconnecting adb: {}'.format(_device))
