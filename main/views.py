from itertools import count
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from . import tools
from .models import *
import json
import time

# Create your views here.


# This funtion is for testing only, please delete this funcion before deploying.
@csrf_exempt
def index(request):
    # return index page
    # return HttpResponse("Hello World")
    if request.method == "GET":
        pass
    elif request.method == "POST":
        pass
    else:
        print("Any thing new?")
    return JsonResponse({"code": 200, "data": "Hello World"}, status = 200, headers = {'Access-Control-Allow-Origin':'*'})

#user login
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
    if request.method == "POST":
        try:
            request_data = json.loads(request.body.decode())
        except Exception as e:
            return JsonResponse({"code": 1003, "message": "INTERNAL_ERROR", "data": {}}, status = 500, headers = {'Access-Control-Allow-Origin':'*'})
        user_name = request_data["user_name"]
        password = request_data["password"]
        if user_name == "Alice" and password == "Bob19937": # should use md5
            status_code = 200
            response_msg = {
                "code": 0,
                "message": "SUCCESS",
                "data": {
                    "id": 1,
                    "user_name": user_name,
                    "token": tools.create_token(user_name)
                }
            }
        else:
            status_code = 400
            response_msg = {
                "code": 4,
                "message": "WRONG_PASSWORD",
                "data": {}
            }
        return JsonResponse(response_msg, status = status_code, headers = {'Access-Control-Allow-Origin':'*'})
    
    return JsonResponse({"code": 1003, "message": "INTERNAL_ERROR", "data": {}}, status = 500, headers = {'Access-Control-Allow-Origin':'*'})

#user register
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
    if request.method == "POST":
        try:
            request_data = json.loads(request.body.decode())
        except Exception as e:
            return JsonResponse({"code": 1003, "message": "INTERNAL_ERROR", "data": {}}, status = 500, headers = {'Access-Control-Allow-Origin':'*'})
        user_name = request_data["user_name"]
        password = request_data["password"]
        if not type(user_name) == str:
            status_code = 400
            response_msg = {
                "code": 2,
                "message": "INVALID_USER_NAME_FORMAT",
                "data": {}
            }
        elif not type(password) == str:
            status_code = 400
            response_msg = {
                "code": 3,
                "message": "INVALID_PASSWORD_FORMAT",
                "data": {}
            }
        else:
            user = user_basic_info.objects.filter(user_name = user_name).first()
            if not user:
                user = user_basic_info(user_name = user_name, password = password)
                try:
                    user.full_clean()
                    user.save()
                    status_code = 200
                    response_msg = {
                        "code": 0,
                        "message": "SUCCESS",
                        "data": {
                            "id": 1,
                            "user_name": user_name,
                            "token": tools.create_token(user_name)
                        }
                    }
                except:
                    return JsonResponse({"code": 1003, "message": "INTERNAL_ERROR", "data": {}}, status = 500, headers = {'Access-Control-Allow-Origin':'*'})
            else:
                status_code = 400
                response_msg = {
                    "code": 1,
                    "message": "USER_NAME_CONFLICT",
                    "data": {}
                }
        return JsonResponse(response_msg, status = status_code, headers = {'Access-Control-Allow-Origin':'*'})
    return JsonResponse({"code": 1003, "message": "INTERNAL_ERROR", "data": {}}, status = 500, headers = {'Access-Control-Allow-Origin':'*'})

# return a news list
@csrf_exempt
def news_response(request):
    """
    response:
    {
        "code": 0,
        "message": "SUCCESS",
        "data": [
            {
                "title": "Breaking News",
                "url": "https://breaking.news",
                "category": "breaking",
                "priority": 1,
                "picture_url": "https://breaking.news/picture.png"
            }
        ]
    }
    """
    if request.method == "GET":
        # do not check token until news recommendation is online.
        # encoded_token = request.META.get("HTTP_AUTHORIZATION")
        # token = tools.decode_token(encoded_token)
        # if token_expired(token):
        #     pass

        newses = []
        news = {
            "title": "Breaking News",
            "url": "https://breaking.news",
            "category": "breaking",
            "priority": 1,
            "picture_url": "https://breaking.news/picture.png"
        }
        newses.append(news)
        return JsonResponse({"code": 0, "message": "SUCCESS", "data": newses}, status = 200, headers = {'Access-Control-Allow-Origin':'*'})

    
    return JsonResponse({"code": 1003, "message": "INTERNAL_ERROR", "data": {}}, status = 500, headers = {'Access-Control-Allow-Origin':'*'})

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
            encoded_token = request.META.get("HTTP_AUTHORIZATION")
            token = tools.decode_token(encoded_token)
            if tools.token_expired(token):
                return JsonResponse({"code": 1001, "message": "UNAUTHORIZED", "data": {}}, status = 401, headers = {'Access-Control-Allow-Origin':'*'})
        except Exception as e:
            return JsonResponse({"code": 1001, "message": "UNAUTHORIZED", "data": {}}, status = 401, headers = {'Access-Control-Allow-Origin':'*'})
        try:
            request_data = json.loads(request.body.decode())
            user_name = request_data["user_name"]
            old_password = request_data["old_password"]
            new_password = request_data["new_password"]
        except Exception as e:
            return JsonResponse({"code": 1003, "message": "INTERNAL_ERROR", "data": {}}, status = 500, headers = {'Access-Control-Allow-Origin':'*'})
        
        # if not user_name == token["user_name"]:
        #     return JsonResponse({"code": 1001, "message": "UNAUTHORIZED", "data": {}}, status = 401, headers = {'Access-Control-Allow-Origin':'*'})
            
        if not old_password == "Bob19937": # should use md5
            status_code = 400
            response_msg = {
                "code": 4,
                "message": "WRONG_PASSWORD",
                "data": {}
            }
        elif not type(new_password) == str: # should use md5
            status_code = 400
            response_msg = {
                "code": 3,
                "message": "INVALID_PASSWORD_FORMAT",
                "data": {}
            }
        else:
            status_code = 200
            response_msg = {"code": 0, "message": "SUCCESS", "data": {}}
        return JsonResponse(response_msg, status = status_code, headers = {'Access-Control-Allow-Origin':'*'})
    return JsonResponse({"code": 1003, "message": "INTERNAL_ERROR", "data": {}}, status = 500, headers = {'Access-Control-Allow-Origin':'*'})
