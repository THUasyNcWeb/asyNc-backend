from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

# Create your views here.


# This funtion is for testing only, please delete this funcion before deploying.
def index(request):
    # return index page
    # return HttpResponse("Hello World")
    if request.method == "GET":
        pass
    elif request.method == "POST":
        pass
    else:
        print("Any thing new?")
    return JsonResponse({"code": 200, "data": "Hello World"})

#user login
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
        user_name = request.POST["user_name"]
        password = request.POST["password"]
        response_msg = {
            "code": 0,
            "message": "SUCCESS",
            "data": {
                "id": 1,
                "user_name": user_name,
                "token": "SECRET_TOKEN"
            }
        }
        return JsonResponse({"code": 200, "data": response_msg})
    
    return JsonResponse({"code": 400, "data": {"code": 4, "message": "WRONG_PASSWORD", "data": {}}})

#user register
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
        user_name = request.POST["user_name"]
        password = request.POST["password"]
        response_msg = {
            "code": 0,
            "message": "SUCCESS",
            "data": {
                "id": 1,
                "user_name": user_name,
                "token": "SECRET_TOKEN"
            }
        }
        return JsonResponse({"code": 200, "data": response_msg})
    
    return JsonResponse({"code": 400, "data": {"code": 1, "message": "USER_NAME_CONFLICT", "data": {}}})

# return a new
def news_response(request):
    """
    response:
    [
        {
            "title":String,
            // 新闻的标题
            "url":String,
            // 新闻的网址
            "category":String,
            // 新闻所属的类别，如政治、生活
            "priority":int,
            // 新闻的优先级，在前端以字号大小加以区分
    		// 现在认为优先级分三类，1代表最高级，2代表次高级，3代表一般级
            // 初步认为仅在“热点”这一类别中有最高级的新闻，整个正文中有且仅有一条最高级
            // "热点"中次高级数目不限，其他类别次高级新闻为2条
            // 所有类别的一般级新闻不限
        }
    ]
    """
    if request.method == "GET":
        token = request.META.get("HTTP_AUTHORIZATION")
        print("token :", token)
        newses = []
        news = {
            "title":"A good titile is all you need.",
            "url":"a.good.titile.is.all.you.need",
            "category":"tutorial",
            "priority":1,
        }
        newses.append(news)
        newses.append(news)
        return JsonResponse({"code": 200, "data": newses})
    elif request.method == "POST":
        print("Not Right.")
    else:
        print("Any thing new?")

    return JsonResponse({"code": 400, "data": {"mes": "String"}})