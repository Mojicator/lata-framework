import json

def get_version():
    with open('lata-config.json') as json_file:
        data = json.load(json_file)
        return data['version']

def boolean_status(bool):
    if bool:
        return 'PASS'
    else:
        return 'FAIL'