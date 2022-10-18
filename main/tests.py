"""
    test.py in django frame work
"""
import time
from django.test import TestCase, Client
from .models import *
from .tools import *

# Create your tests here.


class ToolsTests(TestCase):
    """
        test functions in tools
    """

    def setUp(self):
        """
            set up a test set
        """
        pass

    def test_tools_md5(self):
        """
            test md5 function in tools
        """
        title = "Test"
        content = "test md5 function in tools"

        str_list = ["password", "Bob19937", "Carol48271", "123456"]
        for string in str_list:
            md5_calculator = hashlib.md5()
            md5_calculator.update(string.encode(encoding='UTF-8'))
            self.assertEqual(md5(string), md5_calculator.hexdigest())

    def test_tools_create_token(self):
        """
            test create token function in tools
        """
        title = "Test"
        content = "test create token function in tools"

        user_name_list = ["Alice", "Bob", "Carol", "用户名", "ユーザー名"]
        for user_name in user_name_list:
            self.assertEqual(
                type(create_token(user_name)),
                str
            )
