import unittest

from app import create_app

app = create_app('test')
db = app.db


class TestBase(unittest.TestCase):
    def setUp(self):
        self.app = app
        db.create_all()

    def tearDown(self):
        db.drop_all()
