"""
    views.py in django frame work
"""
import json
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from elasticsearch import Elasticsearch
from . import tools
from .models import UserBasicInfo
from .responses import internal_error_response, unauthorized_response

# Create your views here.


# This funtion is for testing only, please delete this funcion before deploying.
@csrf_exempt
def index(request):
    """
    This funtion is for testing only, please delete this funcion before deploying.
    Always return code 200
    """
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
            return internal_error_response()
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
            return JsonResponse(
                response_msg,
                status=status_code,
                headers={'Access-Control-Allow-Origin': '*'}
            )
        except Exception as error:
            print(error)
            return internal_error_response()
    return internal_error_response()


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
    if request.method == "POST":
        try:
            request_data = json.loads(request.body.decode())
            user_name = request_data["user_name"]
            password = request_data["password"]
        except Exception as error:
            print(error)
            return internal_error_response()
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
                except Exception as error:
                    print(error)
                    return internal_error_response()
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
    return internal_error_response()


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
        # Do not check token until news recommendation is online:
        # encoded_token = request.META.get("HTTP_AUTHORIZATION")
        # token = tools.decode_token(encoded_token)
        # if token_expired(token):
        #  return 401
        newses = []
        news = {
            "title": "Breaking News",
            "url": "https://breaking.news",
            "category": "breaking",
            "priority": 1,
            "picture_url": "https://breaking.news/picture.png"
        }
        newses.append(news)
        return JsonResponse(
            {"code": 0, "message": "SUCCESS", "data": newses},
            status=200,
            headers={'Access-Control-Allow-Origin': '*'}
        )
    return internal_error_response()


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
            return internal_error_response()

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
            return internal_error_response()
    return internal_error_response()


# Keyword search
class ElasticSearch():
    """
    class for keyword search
    """
    def __init__(self):
        self.client = Elasticsearch(hosts=["localhost"])

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
                                "fields":["title","tags","content"]
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
                "pre_tags": ['<span class="keyWord">'],
                "post_tags": ['</span>'],
                "fields":{
                    "title": {},
                    "content": {}
                }
            }
        }
        response = self.client.search(index="tencent_news", body=query_json)
        return response["hits"]

def get_location(info_str,start_tag='<span class="szz-type"',end_tag='</span>'):
    """
    summary: pass in str
    Returns:
        location_list
    """
    start = len(start_tag)
    end = len(end_tag)

    location_infos = []
    pattern = start_tag+'(.+?)'+end_tag

    for idx, m_res in enumerate(re.finditer(r'{i}'.format(i=pattern), info_str)):
        location_info = []

        if idx == 0:
            location_info.append(m_res.span()[0])
            location_info.append(m_res.span()[1]-(idx+1)*(start+end+1))
        else:
            location_info.append(m_res.span()[0]-idx*(start+end+1))
            location_info.append(m_res.span()[1]-(idx+1)*(start+end+1))

        location_infos.append(location_info)

    return location_infos


@csrf_exempt
def keyword_search(request):
    """
        keyword_search
    """
    if request.method == "POST":
        try:
            encoded_token = request.META.get("HTTP_AUTHORIZATION")
            token = tools.decode_token(encoded_token)
            if tools.token_expired(token):
                return unauthorized_response()
        except Exception as error:
            print(error)
            return unauthorized_response()
        key_word = request.POST.get("query")
        start_page = request.POST.get("page")
        if isinstance(start_page,int) is False:
            return JsonResponse(
                {"code": 5, "message": "INVALID_PAGE", "data": {}},
                status=400,
                headers={'Access-Control-Allow-Origin':'*'}
            )
        elastic_search = ElasticSearch()
        all_news = elastic_search.search(key_words=key_word,start=start_page)
        total_num = all_news['total']['value']
        if total_num % 10 == 0:
            total_num = total_num/10
        else:
            total_num = int(total_num/10) + 1
        news = []
        for new in all_news["hits"]:
            data = new["_source"]
            highlights = new["highlight"]
            # print(highlights)
            title_keywords = []
            keywords = []
            if 'title' in highlights:
                title_highligts = highlights['title']
                title = ""
                for h_title in title_highligts:
                    title.join(h_title)
                title_keywords = get_location(title)
            if 'content' in highlights:
                content_higlights = highlights['content']
                content = ""
                for h_content in content_higlights:
                    content.join(h_content)
                keywords = get_location(content)

            piece_new = {
                "title": data['title'],
                "url": data['news_url'],
                "media": data['media'],
                "category": data['tags'][0],
                "priority": 1,
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
