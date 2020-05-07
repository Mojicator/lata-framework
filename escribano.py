from datetime import datetime
import os

import utils

DIR_NAME = 'output_tests'

def escribano(test_func):
    def writting(*args, **kwargs):
        log = Log(utils.get_version())
        log.star_event()
        result = test_func(*args, **kwargs)
        log.end_event(test_func.__name__, args[1], result)
        print(result)
        return result
    return writting

class Log:
    def __init__(self, version = 'demo'):
        self.version = version
        self.start = ''
        self.end = ''
        self.test_start = ''
        self.test_end = ''
        self.path = self.create_path()

    def create_path(self):
        _path = os.path.join(os.getcwd(), DIR_NAME)
        if not os.path.exists(_path):
            os.mkdir(_path)
        return _path

    def start_test_log(self):
        if not os.path.exists(self.path):
            self.create_path()
        else:
            self.start = datetime.now()
            with open(os.path.join(self.path, 'test-v{0}.txt'.format(self.version)), mode='a') as file:
                file.write('>>>>>>>>>> STARTING TEST - AT: {0} <<<<<<<<<<\n'
                .format(self.start))

    def end_test_log(self):
        if not os.path.exists(self.path):
            self.create_path()
        else:
            self.end = datetime.now()
            _difference = self.end - self.start
            with open(os.path.join(self.path, 'test-v{0}.txt'.format(self.version)), mode='a') as file:
                file.write('>>>>>>>>>> ENDING TEST - AT: {0} -> TIME: {1} <<<<<<<<<<\n'
                .format(self.end, _difference.total_seconds()))


    def star_event(self):
        self.test_start = datetime.now()

    def end_event(self, message, data, result):
        """
        
        """
        self.test_end = datetime.now()
        _difference = self.test_end - self.test_start
        with open(os.path.join(self.path, 'test-v{0}.txt'.format(self.version)), mode='a') as file:
                file.write('::{0} DATA: {1} STATUS: {2}\nDURATION: {3}\n-\n'
                .format(message, data, utils.boolean_status(result), _difference.total_seconds()))