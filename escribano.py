from datetime import datetime
import os

DIR_NAME = 'output_tests'

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

    def end_event(self):
        self.test_end = datetime.now()

    def add_log(self, message):
        """
        By the action given, wirte on a file the test status with all the information.
        :param action: string CALL/WIFI
        """
        with open(os.path.join(self.path, 'test-v{0}.txt'.format(self.version)), mode='a') as file:
                file.write(':: {0}\nSTART AT {1} -> END AT {2}\n-\n'
                .format(message, self.test_start, self.test_end))
