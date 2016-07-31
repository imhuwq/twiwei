import unittest


class Test:
    def __init__(self):
        pass

    def run(self):
        start_dir = 'test'

        tests = unittest.TestLoader().discover(start_dir, pattern='*.py')
        unittest.TextTestRunner(verbosity=2).run(tests)
