"""
    test.py in django frame work
"""
import time
import json
from urllib import request
from django.test import TestCase, Client
from . import tools
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
        tools.TESTING_MODE = True
        self.user_num = 5
        self.user_name_list = ["Alice", "Bob", "Carol", "用户名", "ユーザー名"]

    def test_add_to_read_history_and_get_read_history(self):
        """
            test add_to_read_history() and get_read_history()
        """
        for user_name in self.user_name_list:
            user = UserBasicInfo(user_name=user_name, password=md5("password"))
            for i in range(5):
                add_to_read_history(
                    user=user,
                    news={
                        "id": i,
                        "title": "Breaking News",
                        "media": "Foobar News",
                        "url": "https://breaking.news",
                        "pub_time": "2022-10-21T19:02:16.305Z",
                        "picture_url": "https://breaking.news/picture.png",
                        "content": ""
                    }
                )
            for i in range(5):
                add_to_read_history(
                    user=user,
                    news={
                        "id": i,
                        "title": "Breaking News",
                        "media": "Foobar News",
                        "url": "https://breaking.news",
                        "pub_time": "2022-10-21T19:02:16.305Z",
                        "picture_url": "https://breaking.news/picture.png",
                        "content": ""
                    }
                )
            read_history = get_read_history(user)
            self.assertEqual(len(read_history),5)
            for i in range(5):
                self.assertEqual(read_history[i]["id"],i)

    def test_remove_read_history(self):
        """
            test remove_read_history()
        """
        for user_name in self.user_name_list:
            user = UserBasicInfo(user_name=user_name, password=md5("password"))
            for i in range(5):
                add_to_read_history(
                    user=user,
                    news={
                        "id": i,
                        "title": "Breaking News",
                        "media": "Foobar News",
                        "url": "https://breaking.news",
                        "pub_time": "2022-10-21T19:02:16.305Z",
                        "picture_url": "https://breaking.news/picture.png",
                        "content": ""
                    }
                )
            read_history = get_read_history(user)
            self.assertEqual(len(read_history),5)
            for i in range(5):
                self.assertEqual(read_history[i]["id"],i)
            for i in range(5):
                remove_read_history(user=user, news_id=i)
            read_history = get_read_history(user)
            self.assertEqual(len(read_history),0)

    def test_add_to_readlist_and_get_readlist(self):
        """
            test add_to_readlist() and get_readlist()
        """
        for user_name in self.user_name_list:
            user = UserBasicInfo(user_name=user_name, password=md5("password"))
            for i in range(5):
                add_to_readlist(
                    user=user,
                    news={
                        "id": i,
                        "title": "Breaking News",
                        "media": "Foobar News",
                        "url": "https://breaking.news",
                        "pub_time": "2022-10-21T19:02:16.305Z",
                        "picture_url": "https://breaking.news/picture.png",
                        "content": ""
                    }
                )
            for i in range(5):
                add_to_readlist(
                    user=user,
                    news={
                        "id": i,
                        "title": "Breaking News",
                        "media": "Foobar News",
                        "url": "https://breaking.news",
                        "pub_time": "2022-10-21T19:02:16.305Z",
                        "picture_url": "https://breaking.news/picture.png",
                        "content": ""
                    }
                )
            readlist = get_readlist(user)
            self.assertEqual(len(readlist),5)
            for i in range(5):
                self.assertEqual(readlist[i]["id"],i)

    def test_remove_readlist(self):
        """
            test remove_readlist()
        """
        for user_name in self.user_name_list:
            user = UserBasicInfo(user_name=user_name, password=md5("password"))
            for i in range(5):
                add_to_readlist(
                    user=user,
                    news={
                        "id": i,
                        "title": "Breaking News",
                        "media": "Foobar News",
                        "url": "https://breaking.news",
                        "pub_time": "2022-10-21T19:02:16.305Z",
                        "picture_url": "https://breaking.news/picture.png",
                        "content": ""
                    }
                )
            readlist = get_readlist(user)
            self.assertEqual(len(readlist),5)
            for i in range(5):
                self.assertEqual(readlist[i]["id"],i)
            for i in range(5):
                remove_readlist(user=user, news_id=i)
            readlist = get_readlist(user)
            self.assertEqual(len(readlist),0)

    def test_add_to_favorites_and_get_favorites(self):
        """
            test add_to_favorites() and get_favorites()
        """
        for user_name in self.user_name_list:
            user = UserBasicInfo(user_name=user_name, password=md5("password"))
            for i in range(5):
                add_to_favorites(
                    user=user,
                    news={
                        "id": i,
                        "title": "Breaking News",
                        "media": "Foobar News",
                        "url": "https://breaking.news",
                        "pub_time": "2022-10-21T19:02:16.305Z",
                        "picture_url": "https://breaking.news/picture.png",
                        "content": ""
                    }
                )
            for i in range(5):
                add_to_favorites(
                    user=user,
                    news={
                        "id": i,
                        "title": "Breaking News",
                        "media": "Foobar News",
                        "url": "https://breaking.news",
                        "pub_time": "2022-10-21T19:02:16.305Z",
                        "picture_url": "https://breaking.news/picture.png",
                        "content": ""
                    }
                )
            favorites = get_favorites(user)
            self.assertEqual(len(favorites),5)
            for i in range(5):
                self.assertEqual(favorites[i]["id"],i)

    def test_remove_favorites(self):
        """
            test remove_favorites()
        """
        for user_name in self.user_name_list:
            user = UserBasicInfo(user_name=user_name, password=md5("password"))
            for i in range(5):
                add_to_favorites(
                    user=user,
                    news={
                        "id": i,
                        "title": "Breaking News",
                        "media": "Foobar News",
                        "url": "https://breaking.news",
                        "pub_time": "2022-10-21T19:02:16.305Z",
                        "picture_url": "https://breaking.news/picture.png",
                        "content": ""
                    }
                )
            favorites = get_favorites(user)
            self.assertEqual(len(favorites),5)
            for i in range(5):
                self.assertEqual(favorites[i]["id"],i)
            for i in range(5):
                remove_favorites(user=user, news_id=i)
            favorites = get_favorites(user)
            self.assertEqual(len(favorites),0)

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

        user_id = 0
        for user_name in self.user_name_list:
            self.assertEqual(
                type(create_token(user_name=user_name, user_id=user_id)),
                str
            )
            user_id += 1

    def test_tools_decode_token(self):
        """
            test decode token function in tools
        """
        title = "Test"
        content = "test decode token function in tools"

        user_id = 0
        for user_name in self.user_name_list:
            encoded_token = create_token(user_name=user_name, user_id=user_id)
            self.assertEqual(
                user_name,
                jwt.decode(
                    encoded_token.replace("Bearer ",""),
                    SECRET_KEY,
                    algorithms=["HS256"]
                )["user_name"]
            )
            user_id += 1

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

    def test_tools_add_token_to_white_list(self):
        """
            test add token to white list function in tools
        """
        title = "Tools Test"
        content = "test add_token_to_white_list() function in tools"
        self.assertEqual(type(tools.TOKEN_WHITE_LIST), dict)
        tools.TOKEN_WHITE_LIST = {}
        for user_id in range(self.user_num):
            del_all_token_of_an_user(user_id)
            user_name = self.user_name_list[user_id]
            encoded_token = create_token(user_name=user_name, user_id=user_id)
            encoded_expired_token = "Bearer " + jwt.encode(
                {
                    "id":user_id,
                    "user_name": user_name,
                    "EXPIRE_TIME": time.time() + 0
                },
                SECRET_KEY,
                algorithm="HS256"
            )
            add_token_to_white_list(encoded_token=encoded_expired_token)
            for i in range(2):
                add_token_to_white_list(encoded_token=encoded_token)
            self.assertEqual(len(tools.TOKEN_WHITE_LIST[user_id]), 1)
        self.assertEqual(len(tools.TOKEN_WHITE_LIST.keys()), self.user_num)

    def test_tools_check_token_in_white_list(self):
        """
            test check token in white list function in tools
        """
        title = "Tools Test"
        content = "test check_token_in_white_list() function in tools"
        self.assertEqual(type(tools.TOKEN_WHITE_LIST), dict)
        for user_id in range(self.user_num):
            user_name = self.user_name_list[user_id]
            encoded_token = create_token(user_name=user_name, user_id=user_id)
            encoded_expired_token = "Bearer " + jwt.encode(
                {
                    "id":user_id,
                    "user_name": user_name,
                    "EXPIRE_TIME": time.time() + 0
                },
                SECRET_KEY,
                algorithm="HS256"
            )
            add_token_to_white_list(encoded_token=encoded_token)
            self.assertEqual(check_token_in_white_list(encoded_token), True)
            self.assertEqual(check_token_in_white_list(encoded_expired_token), False)

    def test_tools_del_token_from_white_list(self):
        """
            test del token from white list function in tools
        """
        title = "Tools Test"
        content = "test del_token_from_white_list() function in tools"
        self.assertEqual(type(tools.TOKEN_WHITE_LIST), dict)
        for user_id in range(self.user_num):
            user_name = self.user_name_list[user_id]
            encoded_token = create_token(user_name=user_name, user_id=user_id)
            add_token_to_white_list(encoded_token=encoded_token)
            self.assertEqual(check_token_in_white_list(encoded_token), True)
            del_token_from_white_list(encoded_token=encoded_token)
            self.assertEqual(check_token_in_white_list(encoded_token), False)

    def test_tools_del_all_token_of_an_user(self):
        """
            test del all token of an user function in tools
        """
        title = "Tools Test"
        content = "test del_all_token_of_an_user() function in tools"
        for user_id in range(self.user_num):
            tools.del_all_token_of_an_user(user_id=user_id)
            self.assertEqual(len(tools.TOKEN_WHITE_LIST[user_id]), 0)
            user_name = self.user_name_list[user_id]
            for i in range(5):
                encoded_token = create_token(user_name=user_name, user_id=user_id)
                add_token_to_white_list(encoded_token=encoded_token)
            self.assertEqual(len(tools.TOKEN_WHITE_LIST[user_id]), 5)
            tools.del_all_token_of_an_user(user_id=user_id)
            self.assertEqual(len(tools.TOKEN_WHITE_LIST[user_id]), 0)


class ViewsTests(TestCase):
    """
        test functions in views
    """
    databases = "__all__"

    def setUp(self):
        """
            set up a test set
        """
        tools.TESTING_MODE = True

        self.user_name_list = ["Alice", "Bob", "Carol", "用户名", "uユーザー名"]
        self.user_password = ["Alice123", "password", "pass123456", "123456_-", "Alic_-e12"]
        self.user_tags = ["用户", "Tag", "パスワード"]
        self.user_tags_dict = {"用户": 3, "パスワード": 1, "Tag": 2}
        self.user_id = []
        self.default_avatar = ""
        self.user_num = len(self.user_name_list)
        with open("data/default_avatar.base64", "r", encoding="utf-8") as f:
            self.default_avatar = f.read()
        for i in range(self.user_num):
            user_name = self.user_name_list[i]
            password = self.user_password[i]
            user = UserBasicInfo.objects.create(user_name=user_name, password=md5(password))
            user.tags = self.user_tags_dict
            user.full_clean()
            user.save()
            self.user_id.append(user.id)

    def test_index(self):
        """
            test token expired function in tools
        """
        title = "Test"
        content = "test index page in views"

        response = self.client.post('/index', data=None, content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_login_with_wrong_response_method(self):
        """
            test user login with get method
        """
        for i in range(self.user_num):
            user_name = self.user_name_list[i]
            password = self.user_password[i]

            requests = {
                "user_name": user_name,
                "password": password
            }

            response = self.client.get('/login', data=requests, content_type="application/json")
            self.assertEqual(response.status_code, 404)

    def test_login_with_wrong_data_type(self):
        """
            test user login with wrong data type
        """
        requests = {
            "user_name": "Carol",
            "password": 123456
        }
        response = self.client.post('/login', data=requests, content_type="application/json")
        self.assertEqual(response.status_code, 400)

        requests = {
            "user_name": 666.66,
            "password": "password"
        }
        response = self.client.post('/login', data=requests, content_type="application/json")
        self.assertEqual(response.status_code, 400)

        requests = {
            "username": "Alice",
            "PassWord": "Alice"
        }
        response = self.client.post('/login', data=requests, content_type="application/json")
        self.assertEqual(response.status_code, 500)

    def test_login(self):
        """
            test user login
        """
        for i in range(self.user_num):
            user_name = self.user_name_list[i]
            password = self.user_password[i]

            requests = {
                "user_name": user_name,
                "password": password
            }

            response = self.client.post('/login', data=requests, content_type="application/json")
            self.assertEqual(response.status_code, 200)

    def test_wrong_password(self):
        """
            test login with wrong password
        """
        for i in range(self.user_num):
            user_name = self.user_name_list[i]
            requests = {
                "user_name": user_name,
                "password": "Not_A_Pass"
            }

            response = self.client.post('/login', data=requests, content_type="application/json")
            self.assertEqual(response.status_code, 400)

    def test_no_user(self):
        """
            test user does not exist
        """
        requests = {
            "user_name": "User_Not_Exist",
            "password": "666"
        }

        response = self.client.post('/login', data=requests, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_register_with_wrong_data_type(self):
        """
            test user register with wrong data type
        """
        requests = {
            "user_name": "Carol6654",
            "password": 123456
        }
        response = self.client.post('/register', data=requests, content_type="application/json")
        self.assertEqual(response.status_code, 400)

        requests = {
            "user_name": 666.66,
            "password": "password"
        }
        response = self.client.post('/register', data=requests, content_type="application/json")
        self.assertEqual(response.status_code, 400)

        requests = {
            "username": "Alice",
            "PassWord": "Alice"
        }
        response = self.client.post('/register', data=requests, content_type="application/json")
        self.assertEqual(response.status_code, 500)

    def test_register_with_wrong_response_method(self):
        """
            test user register with get method
        """
        requests = {
            "user_name": "Bob19937",
            "password": "Bob19937"
        }

        response = self.client.get('/register', data=requests, content_type="application/json")
        self.assertEqual(response.status_code, 404)

    def test_user_register(self):
        """
            test user register
        """
        requests = {
            "user_name": "RegBob19937",
            "password": "Bob19937"
        }

        response = self.client.post('/register', data=requests, content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_name_conflict(self):
        """
            test name conflict when registring
        """
        requests = {
            "user_name": "Alice",
            "password": "Bob19937"
        }

        response = self.client.post('/register', data=requests, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_news_response_with_wrong_response_method(self):
        """
            test news response with post method
        """
        response = self.client.post('/allnews', data=None, content_type="application/json")
        self.assertEqual(response.status_code, 404)

    def test_news_response(self):
        """
            test news response
        """
        response = self.client.get('/allnews', data=None, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        news_list = json.loads(response.content)["data"]
        self.assertEqual(type(news_list), list)
        for news in news_list:
            self.assertEqual(type(news), dict)

    def test_user_modify_password(self):
        """
            test user modify password
        """
        for i in range(self.user_num):
            user_name = self.user_name_list[i]
            old_password = self.user_password[i]
            new_password = "new_" + self.user_password[i]

            requests = {
                "user_name": user_name,
                "old_password": old_password,
                "new_password": new_password
            }

            encoded_token = create_token(user_name=user_name, user_id=i)
            add_token_to_white_list(encoded_token)
            self.assertEqual(check_token_in_white_list(encoded_token), True)

            response = self.client.post('/modifypassword', data=requests,
                                        content_type="application/json",
                                        HTTP_AUTHORIZATION=encoded_token)
            self.assertEqual(response.status_code, 200)

            # change back the password
            requests = {
                "user_name": user_name,
                "old_password": new_password,
                "new_password": old_password
            }

            response = self.client.post('/modifypassword', data=requests,
                                        content_type="application/json",
                                        HTTP_AUTHORIZATION=encoded_token)
            self.assertEqual(response.status_code, 200)

    def test_modify_wrong_token(self):
        """
            test modify without token
        """
        for i in range(self.user_num):
            user_name = self.user_name_list[i]
            old_password = self.user_password[i]
            new_password = self.user_password[i] + "new"

            requests = {
                "user_name": user_name,
                "old_password": old_password,
                "new_password": new_password
            }
            encoded_token = create_token(user_name=self.user_name_list[i - 1], user_id=i)
            add_token_to_white_list(encoded_token)
            response = self.client.post('/modifypassword',
                                        data=requests,
                                        content_type="application/json",
                                        HTTP_AUTHORIZATION=encoded_token)

            self.assertEqual(response.status_code, 401)

    def test_modify_user_not_exist(self):
        """
            test modify password when user not exist
        """
        for i in range(self.user_num):
            user_name = self.user_name_list[i] + "new"
            old_password = self.user_password[i]
            new_password = self.user_password[i] + "new"

            requests = {
                "user_name": user_name,
                "old_password": old_password,
                "new_password": new_password
            }
            encoded_token = create_token(user_name=user_name, user_id=i)
            add_token_to_white_list(encoded_token)
            response = self.client.post('/modifypassword', data=requests,
                                        content_type="application/json",
                                        HTTP_AUTHORIZATION=encoded_token)

            self.assertEqual(response.status_code, 400)

    def test_modify_wrong_password(self):
        """
            test modify password when old password is wrong
        """
        for i in range(self.user_num):
            user_name = self.user_name_list[i]
            old_password = self.user_password[i - 1]
            new_password = self.user_password[i] + "new"

            requests = {
                "user_name": user_name,
                "old_password": old_password,
                "new_password": new_password
            }
            encoded_token = create_token(user_name=self.user_name_list[i], user_id=i)
            add_token_to_white_list(encoded_token)
            response = self.client.post('/modifypassword', data=requests,
                                        content_type="application/json",
                                        HTTP_AUTHORIZATION=encoded_token)

            self.assertEqual(response.status_code, 400)

    def test_check_login_state(self):
        """
            test check login state function
        """
        for i in range(self.user_num):
            user_name = self.user_name_list[i]
            encoded_token = create_token(user_name=user_name, user_id=i)
            response = self.client.post('/checklogin', data={},
                                        content_type="application/json",
                                        HTTP_AUTHORIZATION=encoded_token)
            self.assertEqual(response.status_code, 401)
            add_token_to_white_list(encoded_token)
            response = self.client.post('/checklogin', data={},
                                        content_type="application/json",
                                        HTTP_AUTHORIZATION=encoded_token)
            self.assertEqual(response.status_code, 200)

    def test_user_logout(self):
        """
            test user logout function
        """
        for i in range(self.user_num):
            user_name = self.user_name_list[i]
            response = self.client.post('/logout', data={},
                                        content_type="application/json",
                                        HTTP_AUTHORIZATION='')
            self.assertEqual(response.status_code, 401)
            encoded_token = create_token(user_name=user_name, user_id=i)
            response = self.client.post('/logout', data={},
                                        content_type="application/json",
                                        HTTP_AUTHORIZATION=encoded_token)
            self.assertEqual(response.status_code, 401)
            add_token_to_white_list(encoded_token)
            response = self.client.post('/logout', data={},
                                        content_type="application/json",
                                        HTTP_AUTHORIZATION=encoded_token)
            self.assertEqual(response.status_code, 200)
            response = self.client.post('/logout', data={},
                                        content_type="application/json",
                                        HTTP_AUTHORIZATION=encoded_token)
            self.assertEqual(response.status_code, 401)

    def test_modify_username(self):
        """
            test modifyusername api
        """
        for i in range(self.user_num):
            user_name = self.user_name_list[i]
            new_user_name = "new_" + user_name
            encoded_token = create_token(user_name=user_name, user_id=self.user_id[i])
            add_token_to_white_list(encoded_token)

            requests = {
                "old_user_name": user_name,
                "new_user_name": new_user_name
            }
            response = self.client.post('/modifyusername', data=requests,
                                        content_type="application/json",
                                        HTTP_AUTHORIZATION=encoded_token)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["data"]["user_name"], new_user_name)
            self.assertEqual(check_token_in_white_list(encoded_token), False)

    def test_user_info_get_method(self):
        """
            test get method of userinfo api
        """
        response = self.client.get(
            '/userinfo',
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=""
        )
        self.assertEqual(response.status_code, 401)

        for i in range(self.user_num):
            user_name = self.user_name_list[i]
            encoded_token = create_token(user_name=user_name, user_id=self.user_id[i])
            add_token_to_white_list(encoded_token)
            response = self.client.get(
                '/userinfo',
                data={},
                content_type="application/json",
                HTTP_AUTHORIZATION=encoded_token
            )
            response_data = response.json()["data"]
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_data["user_name"], user_name)
            self.assertEqual(isinstance(response_data["signature"], str), True)
            self.assertEqual(isinstance(response_data["mail"], str), True)
            self.assertEqual(isinstance(response_data["avatar"], str), True)
            self.assertEqual(isinstance(response_data["tags"], dict), True)
            self.assertEqual(list(response_data["tags"].keys()), self.user_tags)

    def test_modify_user_info_post_method(self):
        """
            test post method of modifyuserinfo api
        """
        response = self.client.get(
            '/userinfo',
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=""
        )
        self.assertEqual(response.status_code, 401)

        for i in range(self.user_num):
            user_name = self.user_name_list[i]
            encoded_token = create_token(user_name=user_name, user_id=self.user_id[i])
            add_token_to_white_list(encoded_token)
            mail = "mail" + str(i) + "@mail.com"
            signature = "signature" + str(i)
            response = self.client.post(
                '/modifyuserinfo',
                data={
                    "mail": mail,
                    "avatar": "data:image/jpeg;base64,",
                    "signature": signature
                },
                content_type="application/json",
                HTTP_AUTHORIZATION=encoded_token
            )
            response_data = response.json()["data"]
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_data["mail"], mail)
            self.assertEqual(response_data["signature"], signature)
            self.assertEqual(response_data["avatar"], "data:image/jpeg;base64,")
            response = self.client.post(
                '/modifyuserinfo',
                data={
                    "signature": signature + str(i),
                    "avatar": "",
                },
                content_type="application/json",
                HTTP_AUTHORIZATION=encoded_token
            )
            response = self.client.get(
                '/userinfo',
                data={},
                content_type="application/json",
                HTTP_AUTHORIZATION=encoded_token
            )
            response_data = response.json()["data"]
            self.assertEqual(response_data["mail"], mail)
            self.assertEqual(response_data["signature"], signature + str(i))
            self.assertEqual(response_data["avatar"], self.default_avatar)

    def test_modify_user_info_username(self):
        """
            test modify username in modifyuserinfo api
        """
        for i in range(self.user_num):
            user_name = self.user_name_list[i]
            new_user_name = "new_" + user_name
            encoded_token = create_token(user_name=user_name, user_id=self.user_id[i])
            add_token_to_white_list(encoded_token)
            mail = "mail" + str(i) + "@mail.com"
            signature = "signature" + str(i)

            requests = {
                "new_user_name": new_user_name,
                "mail": mail,
                "avatar": "data:image/jpeg;base64,",
                "signature": signature
            }
            response = self.client.post('/modifyuserinfo', data=requests,
                                        content_type="application/json",
                                        HTTP_AUTHORIZATION=encoded_token)
            response_data = response.json()["data"]

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_data["user_name"], new_user_name)
            self.assertEqual(check_token_in_white_list(encoded_token), False)
            self.assertEqual(response_data["mail"], mail)
            self.assertEqual(response_data["signature"], signature)
            self.assertEqual(response_data["avatar"], "data:image/jpeg;base64,")
            self.assertEqual(check_token_in_white_list(response_data['token']), True)


class FavoritesTests(TestCase):
    """
        test functions for favorites
    """
    databases = "__all__"

    def setUp(self):
        """
            set up a test set
        """
        tools.TESTING_MODE = True

        self.test_user_num = 2

        self.user_name_list = ["AliceFTester", "BobFTester"]
        self.user_password = ["AlcieFTester", "password"]
        self.user_tags = ["用户", "Tag", "パスワード"]
        self.user_tags_dict = {"用户": 3, "パスワード": 1, "Tag": 2}
        self.user_id = []
        self.default_avatar = ""
        with open("data/default_avatar.base64", "r", encoding="utf-8") as f:
            self.default_avatar = f.read()
        for i in range(self.test_user_num):
            user_name = self.user_name_list[i]
            password = self.user_password[i]
            user = UserBasicInfo.objects.create(user_name=user_name, password=md5(password))
            user.tags = self.user_tags_dict
            user.full_clean()
            user.save()
            self.user_id.append(user.id)

    def test_post_favorites(self):
        """
            test post favorites
        """
        for i in range(self.test_user_num):
            user_name = self.user_name_list[i]
            encoded_token = create_token(user_name=user_name, user_id=self.user_id[i])
            add_token_to_white_list(encoded_token)
            news_id_list = []
            response_data = []
            for news_id in range(1,16):
                response = self.client.post(
                    '/favorites?id={news_id}'.format(news_id=str(news_id)),
                    data={},
                    content_type="application/json",
                    HTTP_AUTHORIZATION=encoded_token
                )
                if response.status_code == 200:
                    news_id_list.append(news_id)
                    response_data = response.json()["data"]
                else:
                    self.assertEqual(response.status_code, 404)
            user = UserBasicInfo.objects.get(user_name=user_name)
            favorites = get_favorites(user)
            self.assertEqual(len(favorites), len(news_id_list))
            for i in range(len(news_id_list)):
                self.assertEqual(bool(int(favorites[i]["id"]) in news_id_list), True)
            if response_data["news"]:
                self.assertEqual(len(response_data["news"]), min(10, len(news_id_list)))
                for news in response_data["news"]:
                    self.assertEqual(type(news["id"]), int)

    def test_get_favorites(self):
        """
            test post favorites
        """
        for i in range(self.test_user_num):
            user_name = self.user_name_list[i]
            encoded_token = create_token(user_name=user_name, user_id=self.user_id[i])
            add_token_to_white_list(encoded_token)
            user = UserBasicInfo.objects.get(user_name=user_name)
            tools.clear_favorites(user)
            for news_id in range(1, 50 + 1):
                add_to_favorites(
                    user=user,
                    news={
                        "id": news_id,
                        "title": "Breaking News",
                        "media": "Foobar News",
                        "url": "https://breaking.news",
                        "pub_time": "2022-10-21T19:02:16.305Z",
                        "picture_url": "https://breaking.news/picture.png",
                        "content": ""
                    }
                )
            for page in range(5):
                response = self.client.get(
                    '/favorites?page={page}'.format(page=page + 1),
                    data={},
                    content_type="application/json",
                    HTTP_AUTHORIZATION=encoded_token
                )
                self.assertEqual(response.status_code, 200)
                response_data = response.json()["data"]
                self.assertEqual(len(response_data["news"]), 10)
                for news in response_data["news"]:
                    self.assertEqual(type(news["id"]), int)
                    begin = page * tools.FAVORITES_PRE_PAGE
                    end = (page + 1) * tools.FAVORITES_PRE_PAGE
                    self.assertEqual(
                        bool(begin <= news["id"] <= end),
                        True
                    )

    def test_delete_favorites(self):
        """
            test delete favorites
        """
        for i in range(self.test_user_num):
            user_name = self.user_name_list[i]
            encoded_token = create_token(user_name=user_name, user_id=self.user_id[i])
            add_token_to_white_list(encoded_token)
            user = UserBasicInfo.objects.get(user_name=user_name)
            tools.clear_favorites(user)
            favorites = get_favorites(user)
            self.assertEqual(len(favorites), 0)
            for news_id in range(1, 10 + 1):
                add_to_favorites(
                    user=user,
                    news={
                        "id": news_id,
                        "title": "Breaking News",
                        "media": "Foobar News",
                        "url": "https://breaking.news",
                        "pub_time": "2022-10-21T19:02:16.305Z",
                        "picture_url": "https://breaking.news/picture.png",
                        "content": ""
                    }
                )
            favorites = get_favorites(user)
            self.assertEqual(len(favorites),10)

            for news_id in range(1, 10 + 1):
                response = self.client.delete(
                    '/favorites?id={news_id}'.format(news_id=str(news_id)),
                    data={},
                    content_type="application/json",
                    HTTP_AUTHORIZATION=encoded_token
                )
                self.assertEqual(response.status_code, 200)
                response_data = response.json()["data"]
                self.assertEqual(len(response_data["news"]), 10 - news_id)
            user = UserBasicInfo.objects.get(user_name=user_name)
            favorites = get_favorites(user)
            self.assertEqual(len(favorites), 0)


class ReadlistTests(TestCase):
    """
        test functions for readlist
    """
    databases = "__all__"

    def setUp(self):
        """
            set up a test set
        """

        self.test_user_num = 2

        self.user_name_list = ["AliceRTester", "BobRTester"]
        self.user_password = ["Alcie", "password"]
        self.user_tags = ["用户", "Tag", "パスワード"]
        self.user_tags_dict = {"用户": 3, "パスワード": 1, "Tag": 2}
        self.user_id = []
        self.default_avatar = ""
        with open("data/default_avatar.base64", "r", encoding="utf-8") as f:
            self.default_avatar = f.read()
        for i in range(self.test_user_num):
            user_name = self.user_name_list[i]
            password = self.user_password[i]
            user = UserBasicInfo.objects.create(user_name=user_name, password=md5(password))
            user.tags = self.user_tags_dict
            user.full_clean()
            user.save()
            self.user_id.append(user.id)

    def test_post_readlist(self):
        """
            test post readlist
        """
        for i in range(self.test_user_num):
            user_name = self.user_name_list[i]
            encoded_token = create_token(user_name=user_name, user_id=self.user_id[i])
            add_token_to_white_list(encoded_token)
            news_id_list = []
            response_data = []
            for news_id in range(1,16):
                response = self.client.post(
                    '/readlater?id={news_id}'.format(news_id=str(news_id)),
                    data={},
                    content_type="application/json",
                    HTTP_AUTHORIZATION=encoded_token
                )
                if response.status_code == 200:
                    news_id_list.append(news_id)
                    response_data = response.json()["data"]
                else:
                    self.assertEqual(response.status_code, 404)
            user = UserBasicInfo.objects.get(user_name=user_name)
            readlist = get_readlist(user)
            self.assertEqual(len(readlist), len(news_id_list))
            for i in range(len(news_id_list)):
                self.assertEqual(bool(int(readlist[i]["id"]) in news_id_list), True)
            if response_data["news"]:
                self.assertEqual(len(response_data["news"]), min(10, len(news_id_list)))
                for news in response_data["news"]:
                    self.assertEqual(type(news["id"]), int)

    def test_get_readlist(self):
        """
            test post readlist
        """
        for i in range(self.test_user_num):
            user_name = self.user_name_list[i]
            encoded_token = create_token(user_name=user_name, user_id=self.user_id[i])
            add_token_to_white_list(encoded_token)
            user = UserBasicInfo.objects.get(user_name=user_name)
            tools.clear_readlist(user)
            for news_id in range(1, 50 + 1):
                add_to_readlist(
                    user=user,
                    news={
                        "id": news_id,
                        "title": "Breaking News",
                        "media": "Foobar News",
                        "url": "https://breaking.news",
                        "pub_time": "2022-10-21T19:02:16.305Z",
                        "picture_url": "https://breaking.news/picture.png",
                        "content": ""
                    }
                )
            for page in range(5):
                response = self.client.get(
                    '/readlater?page={page}'.format(page=page + 1),
                    data={},
                    content_type="application/json",
                    HTTP_AUTHORIZATION=encoded_token
                )
                self.assertEqual(response.status_code, 200)
                response_data = response.json()["data"]
                self.assertEqual(len(response_data["news"]), 10)
                for news in response_data["news"]:
                    self.assertEqual(type(news["id"]), int)
                    begin = page * tools.FAVORITES_PRE_PAGE
                    end = (page + 1) * tools.FAVORITES_PRE_PAGE
                    self.assertEqual(
                        bool(begin <= news["id"] <= end),
                        True
                    )

    def test_delete_readlist(self):
        """
            test delete readlist
        """
        for i in range(self.test_user_num):
            user_name = self.user_name_list[i]
            encoded_token = create_token(user_name=user_name, user_id=self.user_id[i])
            add_token_to_white_list(encoded_token)
            user = UserBasicInfo.objects.get(user_name=user_name)
            tools.clear_readlist(user)
            readlist = get_readlist(user)
            self.assertEqual(len(readlist), 0)
            for news_id in range(1, 10 + 1):
                add_to_readlist(
                    user=user,
                    news={
                        "id": news_id,
                        "title": "Breaking News",
                        "media": "Foobar News",
                        "url": "https://breaking.news",
                        "pub_time": "2022-10-21T19:02:16.305Z",
                        "picture_url": "https://breaking.news/picture.png",
                        "content": ""
                    }
                )
            readlist = get_readlist(user)
            self.assertEqual(len(readlist),10)

            for news_id in range(1, 10 + 1):
                response = self.client.delete(
                    '/readlater?id={news_id}'.format(news_id=str(news_id)),
                    data={},
                    content_type="application/json",
                    HTTP_AUTHORIZATION=encoded_token
                )
                self.assertEqual(response.status_code, 200)
                response_data = response.json()["data"]
                self.assertEqual(len(response_data["news"]), 10 - news_id)
            user = UserBasicInfo.objects.get(user_name=user_name)
            readlist = get_readlist(user)
            self.assertEqual(len(readlist), 0)


class ReadHistoryTests(TestCase):
    """
        test functions for read history
    """
    databases = "__all__"

    def setUp(self):
        """
            set up a test set
        """

        self.test_user_num = 2

        self.user_name_list = ["AliceHTester", "BobHTester"]
        self.user_password = ["Alcie", "password"]
        self.user_tags = ["用户", "Tag", "パスワード"]
        self.user_tags_dict = {"用户": 3, "パスワード": 1, "Tag": 2}
        self.user_id = []
        self.default_avatar = ""
        with open("data/default_avatar.base64", "r", encoding="utf-8") as f:
            self.default_avatar = f.read()
        for i in range(self.test_user_num):
            user_name = self.user_name_list[i]
            password = self.user_password[i]
            user = UserBasicInfo.objects.create(user_name=user_name, password=md5(password))
            user.tags = self.user_tags_dict
            user.full_clean()
            user.save()
            self.user_id.append(user.id)

    def test_post_read_history(self):
        """
            test post read history
        """
        for i in range(self.test_user_num):
            user_name = self.user_name_list[i]
            encoded_token = create_token(user_name=user_name, user_id=self.user_id[i])
            add_token_to_white_list(encoded_token)
            news_id_list = []
            response_data = []
            for news_id in range(1,16):
                response = self.client.post(
                    '/history?id={news_id}'.format(news_id=str(news_id)),
                    data={},
                    content_type="application/json",
                    HTTP_AUTHORIZATION=encoded_token
                )
                if response.status_code == 200:
                    news_id_list.append(news_id)
                    response_data = response.json()["data"]
                else:
                    self.assertEqual(response.status_code, 404)
            user = UserBasicInfo.objects.get(user_name=user_name)
            read_history = get_read_history(user)
            self.assertEqual(len(read_history), len(news_id_list))
            for i in range(len(news_id_list)):
                self.assertEqual(bool(int(read_history[i]["id"]) in news_id_list), True)
            if response_data["news"]:
                self.assertEqual(len(response_data["news"]), min(10, len(news_id_list)))
                for news in response_data["news"]:
                    self.assertEqual(type(news["id"]), int)

    def test_get_read_history(self):
        """
            test post read history
        """
        for i in range(self.test_user_num):
            user_name = self.user_name_list[i]
            encoded_token = create_token(user_name=user_name, user_id=self.user_id[i])
            add_token_to_white_list(encoded_token)
            user = UserBasicInfo.objects.get(user_name=user_name)
            tools.clear_read_history(user)
            for news_id in range(1, 50 + 1):
                add_to_read_history(
                    user=user,
                    news={
                        "id": news_id,
                        "title": "Breaking News",
                        "media": "Foobar News",
                        "url": "https://breaking.news",
                        "pub_time": "2022-10-21T19:02:16.305Z",
                        "picture_url": "https://breaking.news/picture.png",
                        "content": ""
                    }
                )
            for page in range(5):
                response = self.client.get(
                    '/history?page={page}'.format(page=page + 1),
                    data={},
                    content_type="application/json",
                    HTTP_AUTHORIZATION=encoded_token
                )
                self.assertEqual(response.status_code, 200)
                response_data = response.json()["data"]
                self.assertEqual(len(response_data["news"]), 10)
                for news in response_data["news"]:
                    self.assertEqual(type(news["id"]), int)
                    begin = page * tools.FAVORITES_PRE_PAGE
                    end = (page + 1) * tools.FAVORITES_PRE_PAGE
                    self.assertEqual(
                        bool(begin <= news["id"] <= end),
                        True
                    )

    def test_delete_read_history(self):
        """
            test delete read_history
        """
        for i in range(self.test_user_num):
            user_name = self.user_name_list[i]
            encoded_token = create_token(user_name=user_name, user_id=self.user_id[i])
            add_token_to_white_list(encoded_token)
            user = UserBasicInfo.objects.get(user_name=user_name)
            tools.clear_read_history(user)
            read_history = get_read_history(user)
            self.assertEqual(len(read_history), 0)
            for news_id in range(1, 10 + 1):
                add_to_read_history(
                    user=user,
                    news={
                        "id": news_id,
                        "title": "Breaking News",
                        "media": "Foobar News",
                        "url": "https://breaking.news",
                        "pub_time": "2022-10-21T19:02:16.305Z",
                        "picture_url": "https://breaking.news/picture.png",
                        "content": ""
                    }
                )
            read_history = get_read_history(user)
            self.assertEqual(len(read_history),10)

            for news_id in range(1, 10 + 1):
                response = self.client.delete(
                    '/history?id={news_id}'.format(news_id=str(news_id)),
                    data={},
                    content_type="application/json",
                    HTTP_AUTHORIZATION=encoded_token
                )
                self.assertEqual(response.status_code, 200)
                response_data = response.json()["data"]
                self.assertEqual(len(response_data["news"]), 10 - news_id)
            user = UserBasicInfo.objects.get(user_name=user_name)
            read_history = get_read_history(user)
            self.assertEqual(len(read_history), 0)
