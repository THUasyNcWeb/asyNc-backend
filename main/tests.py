"""
    test.py in django frame work
"""
import time
from urllib import request
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
        self.user_name_list = ["Alice", "Bob", "Carol", "用户名", "ユーザー名"]

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

        for user_name in self.user_name_list:
            self.assertEqual(
                type(create_token(user_name)),
                str
            )

    def test_tools_decode_token(self):
        """
            test decode token function in tools
        """
        title = "Test"
        content = "test decode token function in tools"

        for user_name in self.user_name_list:
            encoded_token = create_token(user_name)
            self.assertEqual(
                user_name,
                jwt.decode(
                    encoded_token.replace("Bearer ",""),
                    SECRET_KEY,
                    algorithms=["HS256"]
                )["user_name"]
            )

    def test_tools_token_expired(self):
        """
            test token expired function in tools
        """
        title = "Test"
        content = "test token expired function in tools"

        for user_name in self.user_name_list:
            expired_token = {"user_name": user_name,"EXPIRE_TIME": time.time() - 1}
            self.assertEqual(token_expired(expired_token), True)

        for user_name in self.user_name_list:
            unexpired_token = {"user_name": user_name,"EXPIRE_TIME": time.time() + 1}
            self.assertEqual(token_expired(unexpired_token), False)


class ViewsTests(TestCase):
    """
        test functions in tools
    """

    def setUp(self):
        """
            set up a test set
        """

        Alice = UserBasicInfo.objects.create(user_name="Alice", password=md5("Alice"))

    def test_index(self):
        """
            test token expired function in tools
        """
        title = "Test"
        content = "test index page in views"

        response = self.client.post('/index/', data=None, content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        """
            test user login
        """
        requests = {
            "user_name": "Alice",
            "password": "Alice"
        }
        
        response = self.client.post('/login/', data=requests, content_type="application/json")
        self.assertEqual(response.status_code, 200)
    
    def test_wrong_password(self):
        """
            test login with wrong password
        """
        requests = {
            "user_name": "Alice",
            "password": "666"
        }
        
        response = self.client.post('/login/', data=requests, content_type="application/json")
        self.assertEqual(response.status_code, 400)
    
    def test_no_user(self):
        """
            test user does not exist
        """
        requests = {
            "user_name": "Bob",
            "password": "666"
        }
        response = self.client.post('/login/', data=requests, content_type="application/json")
        self.assertEqual(response.status_code, 400)  
        
