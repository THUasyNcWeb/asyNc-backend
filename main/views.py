"""
    views.py in django frame work
"""
import json
import re
from math import ceil
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Document, Date, Keyword, Text, connections, Completion
import jieba

from tinyrpc import RPCClient
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.transports.http import HttpPostClientTransport

from . import tools
from .models import UserBasicInfo
from .responses import *

# Create your views here.


# This funtion is for testing only, please delete this funcion before deploying.
@csrf_exempt
def index(request):
    """
    This funtion is for testing only, please delete this funcion before deploying.
    Always return code 200
    """
    try:
        if request.method == "GET":
            pass
        elif request.method == "POST":
            pass
        else:
            print("Any thing new?")
        return JsonResponse(
            {
                "code": 200,
                "data": "Hello World"
            },
            status=200,
            headers={'Access-Control-Allow-Origin': '*'}
        )
    except Exception as error:
        print(error)
        return internal_error_response(error=str(error))


# user login
@csrf_exempt
def user_login(request):
    """
    request:
    {
        "user_name": "Alice",
        "password": "Bob19937"
    }
    response:
    {
        "code": 0,
        "message": "SUCCESS",
        "data": {
            "id": 1,
            "user_name": "Alice",
            "token": "SECRET_TOKEN"
        }
    }
    """
    try:
        if request.method == "POST":
            try:
                request_data = json.loads(request.body.decode())
                user_name = request_data["user_name"]
                password = request_data["password"]
                if not (isinstance(user_name, str) and isinstance(password, str)):
                    status_code = 400
                    response_msg = {
                        "code": 4,
                        "message": "WRONG_PASSWORD",
                        "data": {}
                    }
                    return JsonResponse(
                        response_msg,
                        status=status_code,
                        headers={'Access-Control-Allow-Origin': '*'}
                    )
            except Exception as error:
                print(error)
                return internal_error_response(error=str(error))
            try:
                user = UserBasicInfo.objects.filter(user_name=user_name).first()
                if not user:  # user name not existed yet.
                    status_code = 400
                    response_msg = {
                        "code": 4,
                        "message": "WRONG_PASSWORD",
                        "data": {}
                    }
                else:
                    if user.password == tools.md5(password):
                        user_token = tools.create_token(user_id=user.id, user_name=user.user_name)
                        status_code = 200
                        response_msg = {
                            "code": 0,
                            "message": "SUCCESS",
                            "data": {
                                "id": user.id,
                                "user_name": user_name,
                                "token": user_token
                            }
                        }
                        tools.add_token_to_white_list(user_token)
                    else:
                        status_code = 400
                        response_msg = {
                            "code": 4,
                            "message": "WRONG_PASSWORD",
                            "data": {}
                        }
                return JsonResponse(
                    response_msg,
                    status=status_code,
                    headers={'Access-Control-Allow-Origin': '*'}
                )
            except Exception as error:
                print(error)
                return internal_error_response(error=str(error))
    except Exception as error:
        print(error)
        return internal_error_response(error=str(error))
    return not_found_response()


# user register
@csrf_exempt
def user_register(request):
    """
    request:
    {
        "user_name": "Alice",
        "password": "Bob19937"
    }
    response:
    {
        "code": 0,
        "message": "SUCCESS",
        "data": {
            "id": 1,
            "user_name": "Alice",
            "token": "SECRET_TOKEN"
        }
    }
    """
    try:
        if request.method == "POST":
            try:
                request_data = json.loads(request.body.decode())
                user_name = request_data["user_name"]
                password = request_data["password"]
            except Exception as error:
                print(error)
                return internal_error_response(error=str(error))
            if not tools.user_username_checker(user_name):
                status_code = 400
                response_msg = {
                    "code": 2,
                    "message": "INVALID_USER_NAME_FORMAT",
                    "data": {}
                }
            elif not tools.user_password_checker(password):
                status_code = 400
                response_msg = {
                    "code": 3,
                    "message": "INVALID_PASSWORD_FORMAT",
                    "data": {}
                }
            else:
                user = UserBasicInfo.objects.filter(user_name=user_name).first()
                if not user:  # user name not existed yet.
                    user = UserBasicInfo(user_name=user_name, password=tools.md5(password))
                    try:
                        user.full_clean()
                        user.save()
                        user_token = tools.create_token(user_name=user.user_name, user_id=user.id)
                        status_code = 200
                        response_msg = {
                            "code": 0,
                            "message": "SUCCESS",
                            "data": {
                                "id": user.id,
                                "user_name": user_name,
                                "token": user_token
                            }
                        }
                        tools.add_token_to_white_list(user_token)
                    except Exception as error:
                        print(error)
                        return internal_error_response(error=str(error))
                else:  # user name already existed.
                    status_code = 400
                    response_msg = {
                        "code": 1,
                        "message": "USER_NAME_CONFLICT",
                        "data": {}
                    }
            return JsonResponse(
                response_msg,
                status=status_code,
                headers={'Access-Control-Allow-Origin':'*'}
            )
    except Exception as error:
        print(error)
        return internal_error_response(error=str(error))
    return not_found_response()


# modify user info
@csrf_exempt
def modify_user_info(request):
    """
    status_code = 200
    post request:
    {
        "old_user_name": "Alice",
        "new_user_name": "Bob",
        "signature": "This is my signature.",
        "avatar": "",
        "mail": "waifu@diffusion.com"
    }
    """
    try:
        encoded_token = str(request.META.get("HTTP_AUTHORIZATION"))
        user_token = encoded_token
        token = tools.decode_token(encoded_token)
        if not tools.check_token_in_white_list(encoded_token=encoded_token):
            return unauthorized_response()
        user_name = token["user_name"]
        user = UserBasicInfo.objects.filter(user_name=user_name).first()
        if not user:  # user name not existed yet.
            return unauthorized_response()
    except Exception as error:
        print(error)
        return unauthorized_response()

    try:
        if request.method == "POST":
            try:
                request_data = json.loads(request.body.decode())
            except Exception as error:
                print(error)
                return post_data_format_error_response(error)
            if "new_user_name" in request_data:
                try:
                    old_user_name = user_name
                    new_user_name = request_data["new_user_name"]
                except Exception as error:
                    print(error)
                    return internal_error_response(error=str(error))

                if not old_user_name == new_user_name:
                    try:
                        user = UserBasicInfo.objects.filter(user_name=old_user_name).first()
                        if not user:  # user name not existed yet.
                            status_code = 400
                            response_msg = {
                                "code": 6,
                                "message": "WRONG_USERNAME",
                                "data": {}
                            }
                            return JsonResponse(
                                response_msg,
                                status=status_code,
                                headers={'Access-Control-Allow-Origin':'*'}
                            )
                        if not tools.user_username_checker(new_user_name):
                            status_code = 400
                            response_msg = {
                                "code": 3,
                                "message": "INVALID_USERNAME_FORMAT",
                                "data": {}
                            }
                            return JsonResponse(
                                response_msg,
                                status=status_code,
                                headers={'Access-Control-Allow-Origin':'*'}
                            )
                        tools.del_all_token_of_an_user(user_id=user.id)
                        user.user_name = new_user_name
                        user.full_clean()
                        user.save()
                        user_token = tools.create_token(user_id=user.id, user_name=user.user_name)
                        tools.add_token_to_white_list(encoded_token=user_token)
                    except Exception as error:
                        print(error)
                        return internal_error_response(error=str(error))

            if "avatar" in request_data:
                user.avatar = request_data["avatar"]
            if "mail" in request_data:
                user.mail = request_data["mail"]
            if "signature" in request_data:
                user.signature = request_data["signature"]
            try:
                user.full_clean()
                user.save()
            except Exception as error:
                print(error)
                return post_data_format_error_response(error)
            return tools.return_user_info(user=user, user_token=user_token)
    except Exception as error:
        print(error)
        return internal_error_response(error=str(error))
    return not_found_response()


# return user info
@csrf_exempt
def user_info(request):
    """
    status_code = 200
    post request:
    {
        "signature": "This is my signature.",
        "avatar": "",
        "mail": "waifu@diffusion.com"
    }
    response:
    {
        "code": 0,
        "message": "SUCCESS",
        "data": {
            "id": 1,
            "user_name": "Bob",
            "signature": "This is my signature.",
            "tags": [
                "C++",
                "中年",
                "アニメ"
            ],
            "mail": "waifu@diffusion.com",
            "avatar": "",
        }
    }
    """
    try:
        encoded_token = str(request.META.get("HTTP_AUTHORIZATION"))
        token = tools.decode_token(encoded_token)
        if not tools.check_token_in_white_list(encoded_token=encoded_token):
            return unauthorized_response()
        user_name = token["user_name"]
        user = UserBasicInfo.objects.filter(user_name=user_name).first()
        if not user:  # user name not existed yet.
            return unauthorized_response()
    except Exception as error:
        print(error)
        return unauthorized_response()

    try:
        if request.method == "GET":
            return tools.return_user_info(user=user)
    except Exception as error:
        print(error)
        return internal_error_response(error=str(error))
    return not_found_response()


# return a news list
@csrf_exempt
def user_read_history(request):
    """
        add, get, remove user read history
        news format:
        {
            "id": 114,
            "title": "Breaking News",
            "media": "Foobar News",
            "url": "https://breaking.news",
            "pub_time": "2022-10-21T19:02:16.305Z",
            "picture_url": "https://breaking.news/picture.png"
        }
    """
    try:
        encoded_token = str(request.META.get("HTTP_AUTHORIZATION"))
        token = tools.decode_token(encoded_token)
        if not tools.check_token_in_white_list(encoded_token=encoded_token):
            return unauthorized_response()
        user_name = token["user_name"]
        user = UserBasicInfo.objects.filter(user_name=user_name).first()
        if not user:  # user name not existed yet.
            return unauthorized_response()
    except Exception as error:
        print(error)
        return unauthorized_response()

    if request.method == "POST":
        try:
            news_id = int(request.GET.get("id"))
        except Exception as error:
            print(error)
            return news_not_found(error="[URL FORMAT ERROR IN READ HISTORY]:\n" + str(error))
        try:
            db_news_list = tools.get_data_from_db(
                connection=tools.CRAWLER_DB_CONNECTION,
                filter_command="id={id}".format(id=news_id),
                select=["title","news_url","first_img_url","media","pub_time","id"],
                limit=200
            )
            if len(db_news_list) == 0:
                return news_not_found(error="[id not found]:\n")

            user_favorites_dict = tools.get_user_favorites_dict(user=user)
            user_readlist_dict = tools.get_user_readlist_dict(user=user)

            for news in db_news_list:
                tools.add_to_read_history(
                    user=user,
                    news={
                        "id": int(news["id"]),
                        "title": news["title"],
                        "media": news["media"],
                        "url": news["news_url"],
                        "pub_time": str(news["pub_time"]),
                        "picture_url": news["first_img_url"],
                        "is_favorite": bool(
                            tools.in_favorite_check(user_favorites_dict, int(news["id"]))
                        ),
                        "is_readlater": bool(
                            tools.in_favorite_check(user_readlist_dict, int(news["id"]))
                        ),
                    }
                )

            read_history_list, pages = tools.user_read_history_pages(user, 0)
            return JsonResponse(
                {"code": 0, "message": "SUCCESS", "data": {
                    "page_count": pages,
                    "news": read_history_list
                }},
                status=200,
                headers={'Access-Control-Allow-Origin': '*'}
            )
        except Exception as error:
            print(error)
            return internal_error_response(error="[db error]" + str(error))

    if request.method == "GET":
        try:
            page = int(request.GET.get("page"))
        except Exception as error:
            print(error)
            return invalid_page(error="[URL FORMAT ERROR IN READ HISTORY]:\n" + str(error))
        read_history_list, pages = tools.user_read_history_pages(user, page - 1)
        return JsonResponse(
            {
                "code": 0, "message": "SUCCESS",
                "data": {
                    "page_count": pages,
                    "news": read_history_list
                }
            },
            status=200,
            headers={'Access-Control-Allow-Origin': '*'}
        )

    if request.method == "DELETE":
        try:
            news_id = int(request.GET.get("id"))
        except Exception as error:
            print(error)
            return internal_error_response(
                error="[URL FORMAT ERROR IN READ HISTORY]:\n" + str(error)
            )
        status = tools.remove_read_history(user=user, news_id=news_id)
        if not status:
            return news_not_found(error="[id not found in user's read history list]:\n")
        read_history_list, pages = tools.user_read_history_pages(user, 0)
        return JsonResponse(
            {"code": 0, "message": "SUCCESS", "data": {
                "page_count": pages,
                "news": read_history_list
            }},
            status=200,
            headers={'Access-Control-Allow-Origin': '*'}
        )
    return not_found_response()


# return a news list
@csrf_exempt
def user_readlater(request):
    """
        add, get, remove user readlist
        news format:
        {
            "id": 114,
            "title": "Breaking News",
            "media": "Foobar News",
            "url": "https://breaking.news",
            "pub_time": "2022-10-21T19:02:16.305Z",
            "picture_url": "https://breaking.news/picture.png"
        }
    """
    try:
        encoded_token = str(request.META.get("HTTP_AUTHORIZATION"))
        token = tools.decode_token(encoded_token)
        if not tools.check_token_in_white_list(encoded_token=encoded_token):
            return unauthorized_response()
        user_name = token["user_name"]
        user = UserBasicInfo.objects.filter(user_name=user_name).first()
        if not user:  # user name not existed yet.
            return unauthorized_response()
    except Exception as error:
        print(error)
        return unauthorized_response()

    if request.method == "POST":
        try:
            news_id = int(request.GET.get("id"))
        except Exception as error:
            print(error)
            return news_not_found(error="[URL FORMAT ERROR IN READLATER]:\n" + str(error))
        try:
            db_news_list = tools.get_data_from_db(
                connection=tools.CRAWLER_DB_CONNECTION,
                filter_command="id={id}".format(id=news_id),
                select=["title","news_url","first_img_url","media","pub_time","id"],
                limit=200
            )
            if len(db_news_list) == 0:
                return news_not_found(error="[id not found]:\n")

            user_favorites_dict = tools.get_user_favorites_dict(user=user)
            user_readlist_dict = tools.get_user_readlist_dict(user=user)

            for news in db_news_list:
                tools.add_to_readlist(
                    user=user,
                    news={
                        "id": int(news["id"]),
                        "title": news["title"],
                        "media": news["media"],
                        "url": news["news_url"],
                        "pub_time": str(news["pub_time"]),
                        "picture_url": news["first_img_url"],
                        "is_favorite": bool(
                            tools.in_favorite_check(user_favorites_dict, int(news["id"]))
                        ),
                        "is_readlater": bool(
                            tools.in_favorite_check(user_readlist_dict, int(news["id"]))
                        ),
                    }
                )

            readlist_list, pages = tools.user_readlist_pages(user, 0)
            return JsonResponse(
                {"code": 0, "message": "SUCCESS", "data": {
                    "page_count": pages,
                    "news": readlist_list
                }},
                status=200,
                headers={'Access-Control-Allow-Origin': '*'}
            )
        except Exception as error:
            print(error)
            return internal_error_response(error="[db error]" + str(error))

    if request.method == "GET":
        try:
            page = int(request.GET.get("page"))
        except Exception as error:
            print(error)
            return invalid_page(error="[URL FORMAT ERROR IN READLATER]:\n" + str(error))
        readlist_list, pages = tools.user_readlist_pages(user, page - 1)
        return JsonResponse(
            {
                "code": 0, "message": "SUCCESS",
                "data": {
                    "page_count": pages,
                    "news": readlist_list
                }
            },
            status=200,
            headers={'Access-Control-Allow-Origin': '*'}
        )

    if request.method == "DELETE":
        try:
            news_id = int(request.GET.get("id"))
        except Exception as error:
            print(error)
            return internal_error_response(error="[URL FORMAT ERROR IN READLATER]:\n" + str(error))
        status = tools.remove_readlist(user=user, news_id=news_id)
        if not status:
            return news_not_found(error="[id not found in user's readlist list]:\n")
        readlist_list, pages = tools.user_readlist_pages(user, 0)
        return JsonResponse(
            {"code": 0, "message": "SUCCESS", "data": {
                "page_count": pages,
                "news": readlist_list
            }},
            status=200,
            headers={'Access-Control-Allow-Origin': '*'}
        )
    return not_found_response()


# return a news list
@csrf_exempt
def user_favorites(request):
    """
        add, get, remove user favorites
        news format:
        {
            "id": 114,
            "title": "Breaking News",
            "media": "Foobar News",
            "url": "https://breaking.news",
            "pub_time": "2022-10-21T19:02:16.305Z",
            "picture_url": "https://breaking.news/picture.png"
        }
    """
    try:
        encoded_token = str(request.META.get("HTTP_AUTHORIZATION"))
        token = tools.decode_token(encoded_token)
        if not tools.check_token_in_white_list(encoded_token=encoded_token):
            return unauthorized_response()
        user_name = token["user_name"]
        user = UserBasicInfo.objects.filter(user_name=user_name).first()
        if not user:  # user name not existed yet.
            return unauthorized_response()
    except Exception as error:
        print(error)
        return unauthorized_response()
    # try:
    if request.method == "POST":
        try:
            news_id = int(request.GET.get("id"))
        except Exception as error:
            print(error)
            return news_not_found(error="[URL FORMAT ERROR]:\n" + str(error))
        try:
            db_news_list = tools.get_data_from_db(
                connection=tools.CRAWLER_DB_CONNECTION,
                filter_command="id={id}".format(id=news_id),
                select=["title","news_url","first_img_url","media","pub_time","id"],
                limit=200
            )
            if len(db_news_list) == 0:
                return news_not_found(error="[id not found]:\n")

            user_favorites_dict = tools.get_user_favorites_dict(user=user)
            user_readlist_dict = tools.get_user_readlist_dict(user=user)

            for news in db_news_list:
                tools.add_to_favorites(
                    user=user,
                    news={
                        "id": int(news["id"]),
                        "title": news["title"],
                        "media": news["media"],
                        "url": news["news_url"],
                        "pub_time": str(news["pub_time"]),
                        "picture_url": news["first_img_url"],
                        "is_favorite": bool(
                            tools.in_favorite_check(user_favorites_dict, int(news["id"]))
                        ),
                        "is_readlater": bool(
                            tools.in_favorite_check(user_readlist_dict, int(news["id"]))
                        ),
                    }
                )

            favorites_list, pages = tools.user_favorites_pages(user, 0)
            return JsonResponse(
                {"code": 0, "message": "SUCCESS", "data": {
                    "page_count": pages,
                    "news": favorites_list
                }},
                status=200,
                headers={'Access-Control-Allow-Origin': '*'}
            )
        except Exception as error:
            print(error)
            return internal_error_response(error="[db error]" + str(error))
    if request.method == "GET":
        try:
            page = int(request.GET.get("page"))
        except Exception as error:
            print(error)
            return invalid_page(error="[URL FORMAT ERROR]:\n" + str(error))
        favorites_list, pages = tools.user_favorites_pages(user, page - 1)
        return JsonResponse(
            {
                "code": 0, "message": "SUCCESS",
                "data": {
                    "page_count": pages,
                    "news": favorites_list
                }
            },
            status=200,
            headers={'Access-Control-Allow-Origin': '*'}
        )
    if request.method == "DELETE":
        try:
            news_id = int(request.GET.get("id"))
        except Exception as error:
            print(error)
            return internal_error_response(error="[URL FORMAT ERROR]:\n" + str(error))
        status = tools.remove_favorites(user=user, news_id=news_id)
        if not status:
            return news_not_found(error="[id not found in user's favorites list]:\n")
        favorites_list, pages = tools.user_favorites_pages(user, 0)
        return JsonResponse(
            {"code": 0, "message": "SUCCESS", "data": {
                "page_count": pages,
                "news": favorites_list
            }},
            status=200,
            headers={'Access-Control-Allow-Origin': '*'}
        )
    # except Exception as error:
    #     print(error)
    #     return internal_error_response(error=str(error))
    return not_found_response()


# return a news list
@csrf_exempt
def news_response(request):
    """
    request:
    {
        "category": "ent"
    }
    response:
    {
        "code": 0,
        "message": "SUCCESS",
        "data": [
            {
                "title": "Breaking News",
                "url": "https://breaking.news",
                "picture_url": "https://breaking.news/picture.png",
                "media": "Foobar News",
                "pub_time": "2022-10-21T19:02:16.305Z",
            }
        ]
    }
    news template:
    {
        "title": "Breaking News",
        "url": "https://breaking.news",
        "picture_url": "https://breaking.news/picture.png",
        "media": "Foobar News",
        "pub_time": "2022-10-21T19:02:16.305Z"
    }
    """

    user = tools.get_user_from_request(request)

    if request.method == "GET":
        try:
            news_category = request.GET.get("category")
            print("news_category :", news_category)
        except Exception as error:
            print(error)
            return internal_error_response(error="[URL FORMAT ERROR]:\n" + str(error))

        try:
            with open("config/config.json","r",encoding="utf-8") as config_file:
                config = json.load(config_file)
            connection = tools.connect_to_db(config["crawler-db"])

            if news_category in tools.CATEGORY_FRONT_TO_BACKEND:
                category = tools.CATEGORY_FRONT_TO_BACKEND[news_category]
            else:
                category = tools.CATEGORY_FRONT_TO_BACKEND[""]

            db_news_list = tools.get_data_from_db(
                connection=connection,
                filter_command="category='{category}'".format(category=category),
                select=["title","news_url","first_img_url","media","pub_time","id"],
                order_command="ORDER BY pub_time DESC",
                limit=200
            )

            try:
                user_favorites_dict = tools.get_user_favorites_dict(user=user)
                user_readlist_dict = tools.get_user_readlist_dict(user=user)

                news_list = []
                for news in db_news_list:
                    news_list.append(
                        {
                            "title": news["title"],
                            "url": news["news_url"],
                            "picture_url": news["first_img_url"],
                            "media": news["media"],
                            "pub_time": news["pub_time"],  # .strftime("%y-%m-%dT%H:%M:%SZ"),
                            "id": news["id"],
                            "is_favorite": bool(
                                tools.in_favorite_check(user_favorites_dict, int(news["id"]))
                            ),
                            "is_readlater": bool(
                                tools.in_favorite_check(user_readlist_dict, int(news["id"]))
                            ),
                        }
                    )
            except Exception as error:
                print(error)
                return internal_error_response(
                    error="[Crawler DataBase Format Error]:\n" + str(error)
                )
            tools.close_db_connection(connection=connection)

        except Exception as error:
            print(error)
            return internal_error_response(
                error="[Crawler DataBase Connection Error]:\n" + str(error)
            )

        return JsonResponse(
            {"code": 0, "message": "SUCCESS", "data": news_list},
            status=200,
            headers={'Access-Control-Allow-Origin': '*'}
        )
    return not_found_response()


# modify a user's password
@csrf_exempt
def user_modify_password(request):
    """
    request:
    {
        "user_name": "Alice",
        "old_password": "Bob19937",
        "new_password": "Carol48271"
    }
    """
    if request.method == "POST":
        try:
            encoded_token = str(request.META.get("HTTP_AUTHORIZATION"))
            token = tools.decode_token(encoded_token)
            if not tools.check_token_in_white_list(encoded_token=encoded_token):
                return unauthorized_response()
        except Exception as error:
            print(error)
            return unauthorized_response()
        try:
            request_data = json.loads(request.body.decode())
            user_name = request_data["user_name"]
            old_password = request_data["old_password"]
            new_password = request_data["new_password"]
        except Exception as error:
            print(error)
            return internal_error_response(error=str(error))

        if not user_name == token["user_name"]:
            return unauthorized_response()

        try:
            user = UserBasicInfo.objects.filter(user_name=user_name).first()
            if not user:  # user name not existed yet.
                status_code = 400
                response_msg = {
                    "code": 4,
                    "message": "WRONG_PASSWORD",
                    "data": {}
                }
            else:
                if not tools.md5(old_password) == user.password:
                    status_code = 400
                    response_msg = {
                        "code": 4,
                        "message": "WRONG_PASSWORD",
                        "data": {}
                    }
                elif not tools.user_password_checker(new_password):
                    status_code = 400
                    response_msg = {
                        "code": 3,
                        "message": "INVALID_PASSWORD_FORMAT",
                        "data": {}
                    }
                else:
                    user.password = tools.md5(new_password)
                    user.full_clean()
                    user.save()
                    status_code = 200
                    response_msg = {
                        "code": 0,
                        "message":
                        "SUCCESS",
                        "data": {}
                    }
            return JsonResponse(
                response_msg,
                status=status_code,
                headers={'Access-Control-Allow-Origin':'*'}
            )
        except Exception as error:
            print(error)
            return internal_error_response(error=str(error))
    return internal_error_response()


# modify a user's avatar
@csrf_exempt
def modify_avatar(request):
    """
        request:
            form:
                avatar: bin
    """
    if request.method == "POST":
        try:
            encoded_token = str(request.META.get("HTTP_AUTHORIZATION"))
            token = tools.decode_token(encoded_token)
            if not tools.check_token_in_white_list(encoded_token=encoded_token):
                return unauthorized_response()
            user_name = token["user_name"]
            user = UserBasicInfo.objects.filter(user_name=user_name).first()
            if not user:  # user name not existed yet.
                return unauthorized_response()
        except Exception as error:
            print(error)
            return unauthorized_response()

        if not request.FILES.items():
            return post_data_format_error_response("avatar file not found.")
        for (_, file) in request.FILES.items():
            resized_image = tools.resize_image(file.file)
            user.avatar = "data:image/png;base64," + tools.pil_to_base64(resized_image)
            # print("user.avatar :", user.avatar)
            try:
                user.full_clean()
                user.save()
            except Exception as error:
                print(error)
                return post_data_format_error_response(str(error))
            break
        return tools.return_user_info(user=user)
    return not_found_response()


# modify a user's username
@csrf_exempt
def user_modify_username(request):
    """
    request:
    {
        "old_user_name": "Alice",
        "new_user_name": "Bob"
    }
    response:
    {
        "code": 0,
        "message": "SUCCESS",
        "data": {
            "id": 1,
            "user_name": "Bob",
            "token": "SECRET_TOKEN"
        }
    }
    """
    if request.method == "POST":
        try:
            encoded_token = str(request.META.get("HTTP_AUTHORIZATION"))
            token = tools.decode_token(encoded_token)
            if not tools.check_token_in_white_list(encoded_token=encoded_token):
                return unauthorized_response()
        except Exception as error:
            print(error)
            return unauthorized_response()

        try:
            request_data = json.loads(request.body.decode())
            old_user_name = request_data["old_user_name"]
            new_user_name = request_data["new_user_name"]
        except Exception as error:
            print(error)
            return internal_error_response(error=str(error))

        if not old_user_name == token["user_name"]:
            return unauthorized_response()

        try:
            user = UserBasicInfo.objects.filter(user_name=old_user_name).first()
            if not user:  # user name not existed yet.
                status_code = 400
                response_msg = {
                    "code": 6,
                    "message": "WRONG_USERNAME",
                    "data": {}
                }
            else:
                if not tools.user_username_checker(new_user_name):
                    status_code = 400
                    response_msg = {
                        "code": 3,
                        "message": "INVALID_USERNAME_FORMAT",
                        "data": {}
                    }
                else:
                    tools.del_all_token_of_an_user(user_id=user.id)
                    user.user_name = new_user_name
                    user.full_clean()
                    user.save()
                    user_token = tools.create_token(user_id=user.id, user_name=user.user_name)
                    status_code = 200
                    response_msg = {
                        "code": 0,
                        "message":
                        "SUCCESS",
                        "data": {
                            "id": user.id,
                            "user_name": user.user_name,
                            "token": user_token
                        }
                    }
            return JsonResponse(
                response_msg,
                status=status_code,
                headers={'Access-Control-Allow-Origin':'*'}
            )
        except Exception as error:
            print(error)
            return internal_error_response(error=str(error))

    return internal_error_response()


# check login state
@csrf_exempt
def check_login_state(request):
    """
    request:
    token in 'HTTP_AUTHORIZATION'.
    """
    if request.method == "POST":
        try:
            encoded_token = str(request.META.get("HTTP_AUTHORIZATION"))
            if tools.check_token_in_white_list(encoded_token=encoded_token):
                status_code = 200
                response_msg = {
                    "code": 0,
                    "message": "SUCCESS",
                    "data": {}
                }
                return JsonResponse(
                    response_msg,
                    status=status_code,
                    headers={'Access-Control-Allow-Origin':'*'}
                )
            return unauthorized_response()
        except Exception as error:
            print(error)
            return unauthorized_response()
    return internal_error_response()


# user logout
@csrf_exempt
def user_logout(request):
    """
    request:
    token in 'HTTP_AUTHORIZATION'.
    """
    if request.method == "POST":
        try:
            encoded_token = str(request.META.get("HTTP_AUTHORIZATION"))
            if tools.check_token_in_white_list(encoded_token=encoded_token):
                tools.del_token_from_white_list(encoded_token=encoded_token)
                if not tools.check_token_in_white_list(encoded_token=encoded_token):
                    status_code = 200
                    response_msg = {
                        "code": 0,
                        "message": "SUCCESS",
                        "data": {}
                    }
                    return JsonResponse(
                        response_msg,
                        status=status_code,
                        headers={'Access-Control-Allow-Origin':'*'}
                    )
                return internal_error_response()
            return unauthorized_response()
        except Exception as error:
            print(error)
            return unauthorized_response()
    return internal_error_response()


# Keyword search
class ElasticSearch():
    """
    class for keyword search
    """
    def __init__(self):
        self.client = Elasticsearch(hosts=["43.143.147.5"])

    class ArticleType(Document):
        '''
        Define the article type
        '''
        connections.create_connection(hosts=["43.143.147.5"])
        title = Text(analyzer="ik_max_word", search_analyzer="ik_smart")
        content = Text(analyzer="ik_max_word", search_analyzer="ik_smart")
        tags = Text(analyzer="ik_max_word", search_analyzer="ik_smart")
        category = Text(analyzer="ik_max_word", search_analyzer="ik_smart")
        first_img_url = Keyword()
        news_url = Keyword()
        front_image_path = Keyword()
        media = Keyword()
        create_date = Date()
        suggest = Completion(analyzer="ik_max_word")

        def get_url(self):
            """
            return article's url
            """
            return self.news_url

        def get_content(self):
            """
            return content
            """
            return self.content

        class Index:
            """
            Index to connect
            """
            name = "tencent_news"

            def get_index(self):
                """
                return index's name
                """
                return self.name

            def set_index(self, index_name):
                """
                set index
                """
                self.name = index_name

    def search(self,key_words,sorted_by="_score",operator="or", start=0, size=10):
        """
        Args:
            key_words (str): keywords to search (support multi keywords,
            just put them together and separated by ',')
            sorted_by (str, optional): sorting method "_score": sorted by similarity;
            "create_date":sorted by create_date. "Defaults to "_score".
            operator (str, optional): "and": results must contain all keywords.
            "or":results must contain at least one keyword Defaults to "or".
            start (int, optional): result start from ... . Defaults to 0.
            size (int, optional): the size of response. Defaults to 10.

        Returns:
            json:
            {
                'total': { 'value': 57, 'relation': 'eq' },
                'max_score': 4.4793386,
                'hits': [
                    {
                    '_index': 'tencent_news',
                    '_type': '_doc',
                    '_id': 'https://new.qq.com/rain/a/20221008A000U100',
                    '_score': 4.4793386,
                    '_source': { 'title': '', 'create_date': '2022-10-08T00:00:00', 'news_url': '',
                    'first_img_url': '', 'content': '国庆假日期间，...', 'tags': ['国庆'] },
                    'highlight': { 'content': ['<span class="keyWord">国庆</span>假日期间，.....'] }
                    },
                    .....
                ]
            }
            'hits' has all results (index from start to start+size)
        """
        query_json = {
            # "_source": "title", only show title(for debug)
            "query":
            {
                "bool":
                {
                    "must":[
                        {
                            "multi_match":
                            {
                                "query":key_words,
                                "operator": operator,
                                "fields":["title","content"]
                            }
                        },
                    ]
                }
            },
            "sort":{
                sorted_by:
                {
                    # desc: Descending ; asc: Ascending;
                    "order":"desc"
                }
            },
            "from":start,
            "size":size,
            # highthlight keyword in results
            "highlight":{
                "pre_tags": ['<span class="szz-type">'],
                "post_tags": ['</span>'],
                "fields":{
                    "title": {},
                    "content": {}
                }
            }
        }
        response = self.client.search(index="tencent_news", body=query_json)
        return response["hits"]

    def suggest(self,keywords,excludes):
        """_summary_

        Args:
            keywords (_type_): need to search
            excludes (_type_): exclude words
            include (_type_): must include words

        Returns:
            _type_: list of suggestions
        """
        response = self.client.search(
            index="tencent_news",
            body={
                "size":10,
                "suggest": {
                    "input-suggester": {
                        "prefix": keywords,
                        "completion": {
                            "field": "suggest"
                        }
                    }
                }
            }
        )
        responses = response['suggest']['input-suggester'][0]['options']
        results = []
        for result in responses:
            sentences = re.split(r'(\.|\!|\?|。|！|？|\.{6}|\n|，|_)', str(result['text']))
            flag = True
            for exclude in excludes:
                if sentences[0].find(exclude) != -1:
                    flag = False
            if flag:
                results += [sentences[0]]
        return list(set(results))

    def completion(self,keywords):
        """_summary_

        Args:
            keywords (_type_): words to search
        """
        search = self.ArticleType.search()
        re_data = []
        completion = {
            "field":"suggest",
            "fuzzy":{
                "fuzziness":2
            },
            "size":10
        }
        # print(keywords)
        search = search.suggest('my_suggest',keywords,completion=completion)
        # print(s.to_dict())
        suggestions = search.execute().suggest
        for match in suggestions.my_suggest[0].options:
            source = match._source
            print(source['content'])
            re_data.append(source['title'])
        return re_data


@csrf_exempt
def get_location(info_str,start_tag='<span class="szz-type">',end_tag='</span>'):
    """
    summary: pass in str
    Returns:
        location_list
    """
    start = len(start_tag)
    end = len(end_tag)
    location_infos = []
    pattern = start_tag + '(.+?)' + end_tag
    try:
        for idx,m_res in enumerate(re.finditer(r'{i}'.format(i=pattern), info_str)):
            location_info = []

            if idx == 0:
                location_info.append(m_res.span()[0])
                location_info.append(m_res.span()[1] - (idx + 1) * (start + end))
            else:
                location_info.append(m_res.span()[0] - idx * (start + end))
                location_info.append(m_res.span()[1] - (idx + 1) * (start + end))

            location_infos.append(location_info)

        return location_infos
    except Exception as error:
        print(error)
        return location_infos


@csrf_exempt
def update_tags(username, tags, user_tags_dict):
    """
    update user tags when searching
    """
    if user_tags_dict is None:
        print("None")
        user_tags_dict = {}
    tags_dict = {}
    user_tags = []
    for key in tags:
        tags_dict[key] = tags_dict.get(key,0) + 1
    tags_dict = sorted(tags_dict.items(), key=lambda x: x[1], reverse=True)
    for i in range(3):
        user_tags += [tags_dict[i][0]]
    for key in user_tags:
        user_tags_dict[key] = user_tags_dict.get(key,0) + 1
    try:
        user = UserBasicInfo.objects.filter(user_name=username).first()
        user.tags = user_tags_dict
        user.save()
    except Exception as error:
        print(error)
        print("Update failed!")


@csrf_exempt
def keyword_essearch(request):
    """
        keyword_search
    """
    if request.method == "POST":

        try:
            body = json.loads(request.body)
            key_word = body["query"]
            start_page = int(body["page"]) - 1
            start_page = min(max(start_page, 0),5000)
            if isinstance(start_page,int) is False:
                return JsonResponse(
                    {"code": 5, "message": "INVALID_PAGE", "data": {"page_count": 0, "news": []}},
                    status=400,
                    headers={'Access-Control-Allow-Origin':'*'}
                )
        except Exception as error:
            print(error)
            return JsonResponse(
                {"code": 1005, "message": "INVALID_FORMAT", "data": {"page_count": 0, "news": []}},
                status=400,
                headers={'Access-Control-Allow-Origin':'*'}
            )
        elastic_search = ElasticSearch()
        all_news = elastic_search.search(key_words=key_word,start=start_page)
        total_num = ceil(all_news['total']['value'] / 10)
        if start_page > total_num:
            return JsonResponse(
                {"code": 0, "message": "SUCCESS", "data": {"page_count": 0, "news": []}},
                status=200,
                headers={'Access-Control-Allow-Origin':'*'}
            )
        news = []
        tags = []

        # get user favorites dict
        user = tools.get_user_from_request(request)
        user_favorites_dict = tools.get_user_favorites_dict(user=user)
        user_readlist_dict = tools.get_user_readlist_dict(user=user)

        for new in all_news["hits"]:
            data = new["_source"]
            highlights = new["highlight"]
            title_keywords = []
            keywords = []
            title = ""
            content = data['content']
            if 'title' in highlights:
                for title in highlights['title']:
                    loc_offset = data['title'].find(title.replace('<span class="szz-type">','')
                                                    .replace('</span>',''))
                    for location_info in get_location(title):
                        title_keywords += [[index + loc_offset for index in location_info]]

            if 'content' in highlights:
                content = highlights['content']
                content = "".join(content)

                keywords = get_location(content)

            if "id" not in data:  # 0 stands for no news id
                data["id"] = 0

            piece_new = {
                "title": data['title'],
                "url": data['news_url'],
                "media": data['media'],
                "pub_time": data['create_date'],
                "content": content.replace('<span class="szz-type">','').replace('</span>',''),
                "picture_url": data['first_img_url'],
                "title_keywords": title_keywords,
                "keywords": keywords,
                "is_favorite": bool(
                    tools.in_favorite_check(user_favorites_dict, int(data["id"]))
                ),
                "is_readlater": bool(
                    tools.in_favorite_check(user_readlist_dict, int(data["id"]))
                ),
            }
            news += [piece_new]
            if data['tags'] and isinstance(data['tags'],list) and start_page == 0 \
                    and data['tags'] != [""]:
                tags += data['tags']
        data = {
            "page_count": total_num,
            "news": news
        }
        try:
            encoded_token = str(request.META.get("HTTP_AUTHORIZATION"))
            token = tools.decode_token(encoded_token)
            user_name = token["user_name"]
            user = UserBasicInfo.objects.filter(user_name=user_name).first()
            if user:
                update_tags(user.user_name, tags, user.tags)

        except Exception as error:
            print(error)
        return JsonResponse(
            {"code": 0, "message": "SUCCESS", "data": data},
            status=200,
            headers={'Access-Control-Allow-Origin':'*'}
        )
    return internal_error_response()


@csrf_exempt
def check_contain(title, content, title_keywords, content_keywords, must, must_not):
    """
    Check whether satisfy the need
    """
    try:
        for no_contain in must_not:
            if title.find(no_contain) != -1:
                return False
            if content.find(no_contain) != -1:
                return False

        for yes in must:
            yes_len = len(yes)
            flag = False
            for title_keyword in title_keywords:
                start = title_keyword[0]
                end = start + yes_len
                target = title[start:end]
                if target == yes:
                    flag = True
            if flag is False:
                for content_keyword in content_keywords:
                    start = content_keyword[0]
                    end = start + yes_len
                    target = content[start:end]
                    if target == yes:
                        flag = True
            if flag is False:
                return False
        return True
    except Exception as error:
        print(error)
        return False


@csrf_exempt
def keyword_search(request):
    """
        keyword_search
    """
    if request.method == "POST":

        try:
            body = json.loads(request.body)
            key_word = body["query"]
            include = body["include"]
            exclude = body["exclude"]
            start_page = int(body["page"]) - 1
            start_page = min(max(start_page, 0),5000)
            if isinstance(start_page,int) is False:
                return JsonResponse(
                    {"code": 5, "message": "INVALID_PAGE", "data": {"page_count": 0, "news": []}},
                    status=400,
                    headers={'Access-Control-Allow-Origin':'*'}
                )
        except Exception as error:
            print(error)
            return JsonResponse(
                {"code": 1005, "message": "INVALID_FORMAT", "data": {"page_count": 0, "news": []}},
                status=400,
                headers={'Access-Control-Allow-Origin':'*'}
            )
        with open("config/lucene.json","r",encoding="utf-8") as config_file:
            config = json.load(config_file)
        rpc_client = RPCClient(
            JSONRPCProtocol(),
            HttpPostClientTransport('http://' + config['url'] + ':' + str(config['port']))
        )
        str_server = rpc_client.get_proxy()
        str_server = rpc_client.get_proxy()
        if len(include) != 0 or len(exclude) != 0:
            keyword_list = list(jieba.cut_for_search(key_word))
            include_list = []
            exclude_list = []
            for must in include:
                include_list += jieba.cut_for_search(must)
            for must_not in exclude:
                exclude_list += jieba.cut_for_search(must_not)
            include_list = list(set(include_list))
            exclude_list = list(set(exclude_list))
            all_news = str_server.search_keywords(keyword_list,
                                                  list(include_list),
                                                  list(exclude_list),0)
        else:
            all_news = str_server.search_news(key_word,start_page)
        total_num = ceil(all_news['total'] / 10)
        if start_page > total_num:
            return JsonResponse(
                {"code": 0, "message": "SUCCESS", "data": {"page_count": 0, "news": []}},
                status=200,
                headers={'Access-Control-Allow-Origin':'*'}
            )
        news = []
        tags = []

        # get user favorites dict
        user = tools.get_user_from_request(request)
        user_favorites_dict = {}
        user_favorites_dict = tools.get_user_favorites_dict(user=user)
        user_readlist_dict = tools.get_user_readlist_dict(user=user)

        for new in all_news["news_list"]:
            data = new
            title_keywords = []
            keywords = []
            title = data['title']
            content = data['content']
            title_keywords = get_location(title)
            keywords = get_location(content)
            if content is None:
                content = ""
            if title is None:
                title = ""
            if "id" not in data:  # 0 stands for no news id
                data["id"] = 0
            piece_new = {
                "title": title.replace('<span class="szz-type">','').replace('</span>',''),
                "url": data['url'],
                "media": data['media'],
                "pub_time": data['pub_time'],
                "content": content.replace('<span class="szz-type">','').replace('</span>',''),
                "picture_url": data['picture_url'],
                "title_keywords": title_keywords,
                "keywords": keywords,
                "is_favorite": bool(
                    tools.in_favorite_check(user_favorites_dict, int(data["id"]))
                ),
                "is_readlater": bool(
                    tools.in_favorite_check(user_readlist_dict, int(data["id"]))
                ),
            }
            if len(include) != 0 or len(exclude) != 0:
                if check_contain(piece_new['title'], piece_new['content'],
                                 piece_new['title_keywords'], piece_new['keywords'],
                                 list(include_list), list(exclude_list)) is True:
                    news += [piece_new]
                total_num = ceil(len(news) / 10)
            else:
                news += [piece_new]
            if data['tags'] and isinstance(data['tags'],list) and start_page == 0 \
                    and data['tags'] != [""]:
                tags += data['tags']
        data = {
            "page_count": total_num,
            "news": news
        }
        try:
            encoded_token = str(request.META.get("HTTP_AUTHORIZATION"))
            token = tools.decode_token(encoded_token)
            user_name = token["user_name"]
            user = UserBasicInfo.objects.filter(user_name=user_name).first()
            if user:
                update_tags(user.user_name, tags, user.tags)

        except Exception as error:
            print(error)
        return JsonResponse(
            {"code": 0, "message": "SUCCESS", "data": data},
            status=200,
            headers={'Access-Control-Allow-Origin':'*'}
        )
    return internal_error_response()


@csrf_exempt
def search_suggest(request):
    """
        keyword_search
    """
    if request.method == "POST":
        exclude = []
        try:
            body = json.loads(request.body)
            key_word = body["query"]
            if "exclude" in body:
                exclude = body["exclude"]

        except Exception as error:
            print(error)
            return JsonResponse(
                {"code": 1005, "message": "INVALID_FORMAT", "data": {"page_count": 0, "news": []}},
                status=400,
                headers={'Access-Control-Allow-Origin':'*'}
            )

        esearch = ElasticSearch()
        results = esearch.suggest(key_word,exclude)
        data = {
            "suggestions":results
        }

        return JsonResponse(
            {"code": 0, "message": "SUCCESS", "data": data},
            status=200,
            headers={'Access-Control-Allow-Origin':'*'}
        )
    data = {
        "suggestions":[]
    }
    return JsonResponse(
        {"code": 0, "message": "SUCCESS", "data": data},
        status=200,
        headers={'Access-Control-Allow-Origin':'*'}
    )
