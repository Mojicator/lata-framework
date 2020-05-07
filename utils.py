import json

TGREEN =  '\033[32m' # Green Text
TRED =  '\033[31m' # Red Text
TNOR =  '\033[m' # Reset

def get_version():
    with open('lata-config.json') as json_file:
        data = json.load(json_file)
        return data['version']

def boolean_status(value):
    if value == True:
        return 'PASS'
    else:
        return 'FAIL'