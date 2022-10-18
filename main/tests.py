"""
    test.py in django frame work
"""

from django.test import TestCase, Client
from .models import *
from .tools import *

# Create your tests here.


class UserModelTests(TestCase):
    def setUp(self):
        pass

    def test_tools_md5(self):
        title = "Test"
        content = "test tools.md5 function"

        str_list = ["password", "Bob19937", "Carol48271", "123456"]
        for string in str_list:
            md5_calculator = hashlib.md5()
            md5_calculator.update(string.encode(encoding='UTF-8'))
            self.assertEqual(md5(string), md5_calculator.hexdigest())
