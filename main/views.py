"""
    views.py in django frame work
"""
import json
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from elasticsearch import Elasticsearch
from . import tools
from .models import UserBasicInfo, News
from .responses import internal_error_response, unauthorized_response, not_found_response

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
            if not isinstance(user_name, str):  # format check.
                status_code = 400
                response_msg = {
                    "code": 2,
                    "message": "INVALID_USER_NAME_FORMAT",
                    "data": {}
                }
            elif not isinstance(password, str):  # format check.
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


# return user info
@csrf_exempt
def user_info(request):
    """
    status_code = 200
    response:
    {
        "code": 0,
        "message": "SUCCESS",
        "data": [
            {
                "id": 1,
                "user_name": "Bob",
                "signature": "This is my signature.",
                "tags": [
                    "C++",
                    "中年",
                    "アニメ"
                ]
            }
        ]
    }
    """
    try:
        if request.method == "GET":
            try:
                encoded_token = str(request.META.get("HTTP_AUTHORIZATION"))
                token = tools.decode_token(encoded_token)
                if not tools.check_token_in_white_list(encoded_token=encoded_token):
                    return unauthorized_response()
            except Exception as error:
                print(error)
                return unauthorized_response()

            try:
                user_name = token["user_name"]
                user = UserBasicInfo.objects.filter(user_name=user_name).first()
                if not user:  # user name not existed yet.
                    return unauthorized_response()
                user_tags = []
                if user.tags:
                    user_tags_dict = user.tags
                    for key_value in sorted(
                        user_tags_dict.items(),
                        key=lambda kv:(kv[1], kv[0]),
                        reverse=True
                    ):
                        user_tags.append(key_value[0])

                status_code = 200
                response_msg = {
                    "code": 0,
                    "message": "SUCCESS",
                    "data": {
                        "id": user.id,
                        "user_name": user.user_name,
                        "signature": "This is my signature.",
                        "tags": user_tags[:10]
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
    except Exception as error:
        print(error)
        return internal_error_response(error=str(error))
    return not_found_response()


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
    news template:
    {
        "title": "Breaking News",
        "url": "https://breaking.news",
        "category": "breaking",
        "priority": 1,
        "picture_url": "https://breaking.news/picture.png"
    }
    """
    try:
        if request.method == "GET":
            # Do not check token until news recommendation is online:
            # encoded_token = request.META.get("HTTP_AUTHORIZATION")
            # token = tools.decode_token(encoded_token)
            # if token_expired(token):
            #  return 401
            news_list = []
            for news in News.objects.all().order_by("-pub_time")[0:20]:
                news_list.append(
                    {
                        "title": news.title,
                        "url": news.news_url,
                        "category": news.category,
                        "priority": 1,
                        "picture_url": news.first_img_url
                    }
                )
            return JsonResponse(
                {"code": 0, "message": "SUCCESS", "data": news_list},
                status=200,
                headers={'Access-Control-Allow-Origin': '*'}
            )
    except Exception as error:
        print(error)
        return internal_error_response(error=str(error))
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
                elif not isinstance(new_password, str):
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
                if not isinstance(new_user_name, str):
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


@csrf_exempt
def keyword_search(request):
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
        total_num = all_news['total']['value']
        if total_num % 10 == 0:
            total_num = total_num / 10
        else:
            total_num = int(total_num / 10) + 1
        if start_page > total_num:
            return JsonResponse(
                {"code": 0, "message": "SUCCESS", "data": {"page_count": 0, "news": []}},
                status=200,
                headers={'Access-Control-Allow-Origin':'*'}
            )
        news = []
        for new in all_news["hits"]:
            data = new["_source"]
            try:
                highlights = new["highlight"]
            except Exception as error:
                print(error)
                highlights = {}
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

            piece_new = {
                "title": data['title'],
                "url": data['news_url'],
                "media": data['media'],
                "pub_time": data['create_date'],
                "content": content.replace('<span class="szz-type">','').replace('</span>',''),
                "picture_url": data['first_img_url'],
                "title_keywords": title_keywords,
                "keywords": keywords
            }
            news += [piece_new]
        data = {
            "page_count": total_num,
            "news": news
        }
        return JsonResponse(
            {"code": 0, "message": "SUCCESS", "data": data},
            status=200,
            headers={'Access-Control-Allow-Origin':'*'}
        )
    return internal_error_response()
