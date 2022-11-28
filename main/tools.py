"""
This .py file contains most commenly used tools in views.py

Created by sxx
"""
import math
import hashlib
import time
import base64
import json
import re
import pickle
import datetime
from io import BytesIO

from tinyrpc import RPCClient
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.transports.http import HttpPostClientTransport
import threadpool
import jwt
import psycopg2
from PIL import Image
from django.http import JsonResponse
from .models import UserBasicInfo
from .responses import internal_error_response
from .managers.NewsCache import NewsCache
from .managers.LocalNewsManager import LocalNewsManager
from .managers.DBScanner import DBScanner
from .config import *

CRAWLER_DB_CONNECTION = None
NEWS_CACHE = None
DB_SCANNER = None
THREAD_POOL = None
LOCAL_NEWS_MANAGER = None
SEARCH_CONNECTION = None


def datetime_converter(date_str: str) -> datetime.datetime:
    """
        convert str into datetime
    """
    try:
        if "+" in date_str:
            dt_datetime = datetime.datetime.strptime(
                date_str,
                '%Y-%m-%d %H:%M:%S%z'
            )
        elif "T" in date_str and "Z" in date_str:
            dt_datetime = datetime.datetime.strptime(
                date_str,
                '%Y-%m-%dT%H:%M:%SZ'
            )
        else:
            dt_datetime = datetime.datetime.strptime(
                date_str,
                '%Y-%m-%d %H:%M:%S'
            )
    except Exception as error:
        print("[error in datetime_converter]")
        print(error)
        dt_datetime = datetime.datetime.strptime(
            "1970-01-01 08:00:00",
            '%Y-%m-%d %H:%M:%S'
        )
    return dt_datetime


def get_news_from_db_by_id(news_id: int) -> bool:
    """
        get news from db by id
    """
    if TESTING_MODE:
        with open("data/news_template.pkl", "rb") as file:
            db_news_list = [pickle.load(file)[0]]
        db_news_list[0]["id"] = news_id
        db_news_list[0]["tags"] = []
        # print(db_news_list)
    elif news_id in NEWS_CACHE.newspool:
        db_news_list = [NEWS_CACHE.newspool[news_id]]
    else:
        db_news_list = get_data_from_db(
            connection=CRAWLER_DB_CONNECTION,
            filter_command="id = {id}".format(id=news_id),
            select=[
                "title","news_url","first_img_url","media",
                "pub_time","id","category","content","tags"
            ],
            limit=1
        )
        # for news in db_news_list:
        #     for key in news:
        #         print(type(news[key]))
        # with open("data/news_template.pkl", "wb") as file:
        #     pickle.dump(db_news_list, file)
        # print(db_news_list)
    return db_news_list


def add_to_search_history(user: UserBasicInfo, search_history: dict):
    """
        add a news to user's search history
    """
    if not search_history:
        return
    if not user.search_history:
        user.search_history = []
    if len(user.search_history) >= MAX_USER_SEARCH_HISTORY:
        pop_search_history(user)
    user.search_history.append(search_history)
    user.full_clean()
    user.save()


def get_search_history(user: UserBasicInfo):
    """
        get search history list from a user
    """
    if not user.search_history:
        user.search_history = []
    return user.search_history


def pop_search_history(user: UserBasicInfo) -> dict:
    """
        pop a news from user's search history
    """
    if not user.search_history:
        user.search_history = []
        return False
    search_history = user.search_history.pop(0)
    user.full_clean()
    user.save()
    return search_history


def clear_search_history(user: UserBasicInfo):
    """
        remove all news from user's search history
    """
    user.search_history = []
    user.full_clean()
    user.save()


def get_user_from_request(request):
    """
        Get user from a request.
        Return None if user not found or token not exist.
    """
    user = None
    username = ""
    try:
        encoded_token = str(request.META.get("HTTP_AUTHORIZATION"))
        token = decode_token(encoded_token)
        if check_token_in_white_list(encoded_token=encoded_token):
            username = token["user_name"]
            user = UserBasicInfo.objects.filter(user_name=username).first()
    except Exception as error:
        print("[error]", error)
    return user


def in_favorite_check(favorites: dict, news_id: int):
    """
        check if in favorites list
    """
    if not favorites:
        return False
    if str(news_id) in favorites or news_id in favorites:
        return True
    return False


def get_user_favorites_dict(user: UserBasicInfo):
    """
        get user favorites dict
    """
    if not user:
        print("[Error] user not exist.")
        return {}
    return dict(user.favorites)


def in_readlist_check(readlist: dict, news_id: int):
    """
        check if in favorites list
    """
    if not readlist:
        return False
    if str(news_id) in readlist or news_id in readlist:
        return True
    return False


def get_user_readlist_dict(user: UserBasicInfo):
    """
        get user readlist dict
    """
    if not user:
        print("[Error] user not exist.")
        return {}
    return dict(user.readlist)


def is_english(char: str):
    """
        char is english
    """
    if re.search('[a-z]', char) or re.search('[A-Z]', char):
        return True
    return False


def is_chinese(char: str):
    """
        char is chinese
    """
    return re.match(".*[\u3400-\u4DB5\u4E00-\u9FCB\uF900-\uFA6A].*", char)


def user_username_checker(username: str):
    """
        check user's username
    """
    if not isinstance(username, str):
        return False
    if len(username) > 14:
        return False
    if not (is_english(username[0]) or is_chinese(username[0])):
        return False
    return True


def user_password_checker(password: str):
    """
        check user's password
    """
    if not isinstance(password, str):
        return False
    if not 8 <= len(password) <= 14:
        return False
    if len(re.findall('[-A-Za-z0-9_]',password)) < len(password):
        return False
    return True


def update_to_user_tags(user: UserBasicInfo, tags: list):
    """
        update user tags
    """
    if not user.tags:
        user.tags = {}
    for tag in tags:
        if tag in user.tags:
            user.tags[tag] += 1
        else:
            user.tags[tag] = 1
    user.full_clean()
    user.save()


def add_to_read_history(user: UserBasicInfo, news: dict):
    """
        add a news to user's read history
    """
    if "id" not in news:
        return
    if not user.read_history:
        user.read_history = {}
    if news["tags"]:
        update_to_user_tags(user=user, tags=news["tags"])
    user.read_history[str(news["id"])] = news
    user.full_clean()
    user.save()


def get_read_history(user: UserBasicInfo):
    """
        get read history list from a user
    """
    if not user.read_history:
        user.read_history = {}
    read_history_list = list(user.read_history.values())

    def key_func(news):
        return news["visit_time"] if "visit_time" in news else "1970-01-01T08:00:00Z"
    read_history_list.sort(key=key_func, reverse=True)
    return read_history_list


def remove_read_history(user: UserBasicInfo, news_id):
    """
        remove a news from user's read_history
    """
    if not user.read_history:
        user.read_history = {}
        return False
    if str(news_id) in user.read_history:
        user.read_history.pop(str(news_id))
        user.full_clean()
        user.save()
        return True
    return False


def clear_read_history(user: UserBasicInfo):
    """
        remove all news from user's read history
    """
    user.read_history = {}
    user.full_clean()
    user.save()


def user_read_history_pages(user: UserBasicInfo, page: int):
    """
        read history pages for user
        page start from 0
    """
    if not user.read_history:
        return [], 0
    read_history_page = []
    begin = page * FAVORITES_PRE_PAGE
    end = (page + 1) * FAVORITES_PRE_PAGE
    read_history_list = get_read_history(user)
    read_history_page = read_history_list[begin:end]

    user_favorites_dict = get_user_favorites_dict(user=user)
    user_readlist_dict = get_user_readlist_dict(user=user)

    for news in read_history_page:
        news["is_favorite"] = in_favorite_check(user_favorites_dict, int(news["id"]))
        news["is_readlater"] = in_readlist_check(user_readlist_dict, int(news["id"]))

    return read_history_page, math.ceil(len(read_history_list) / FAVORITES_PRE_PAGE)


def add_to_readlist(user: UserBasicInfo, news: dict):
    """
        add a news to user's readlist
    """
    if "id" not in news:
        return
    if not user.readlist:
        user.readlist = {}

    try:
        LOCAL_NEWS_MANAGER.save_local_news(news)
    except Exception as error:
        print(error)

    user.readlist[str(news["id"])] = news
    user.full_clean()
    user.save()


def get_readlist(user: UserBasicInfo):
    """
        get readlist list from a user
    """
    if not user.readlist:
        user.readlist = {}
    readlist = list(user.readlist.values())

    def key_func(news):
        return news["visit_time"] if "visit_time" in news else "1970-01-01T08:00:00Z"
    readlist.sort(key=key_func, reverse=True)
    return readlist


def remove_readlist(user: UserBasicInfo, news_id):
    """
        remove a news from user's readlist
    """
    if not user.readlist:
        user.readlist = {}
        return False
    if str(news_id) in user.readlist:
        try:
            LOCAL_NEWS_MANAGER.del_local_news(int(news_id))
        except Exception as error:
            print(error)
        user.readlist.pop(str(news_id))
        user.full_clean()
        user.save()
        return True
    return False


def clear_readlist(user: UserBasicInfo):
    """
        remove all news from user's readlist
    """
    if user.favorites:
        for news_id in user.favorites:
            try:
                LOCAL_NEWS_MANAGER.del_local_news(int(news_id))
            except Exception as error:
                print(error)
    user.readlist = {}
    user.full_clean()
    user.save()


def user_readlist_pages(user: UserBasicInfo, page: int):
    """
        readlist pages for user
        page start from 0
    """
    if not user.readlist:
        return [], 0
    readlist_page = []
    begin = page * FAVORITES_PRE_PAGE
    end = (page + 1) * FAVORITES_PRE_PAGE
    readlist_list = get_readlist(user)
    readlist_page = readlist_list[begin:end]

    user_favorites_dict = get_user_favorites_dict(user=user)
    user_readlist_dict = get_user_readlist_dict(user=user)

    for news in readlist_page:
        try:
            ai_news = LOCAL_NEWS_MANAGER.get_one_ai_news(news["id"])
            if "summary" in ai_news:
                news["summary"] = ai_news["summary"]
            else:
                news["summary"] = ""
        except Exception as error:
            print(error)

    for news in readlist_page:
        news["is_favorite"] = in_favorite_check(user_favorites_dict, int(news["id"]))
        news["is_readlater"] = in_readlist_check(user_readlist_dict, int(news["id"]))

    return readlist_page, math.ceil(len(readlist_list) / FAVORITES_PRE_PAGE)


def add_to_favorites(user: UserBasicInfo, news: dict):
    """
        add a news to user's favorites
    """
    if "id" not in news:
        print("[Error] no id in news.")
        return
    if not user.favorites:
        user.favorites = {}

    try:
        LOCAL_NEWS_MANAGER.save_local_news(news)
    except Exception as error:
        print(error)

    user.favorites[str(news["id"])] = news
    user.full_clean()
    user.save()


def get_favorites(user: UserBasicInfo):
    """
        get favorites list from a user
    """
    if not user.favorites:
        user.favorites = {}
    favorites_list = list(user.favorites.values())

    def key_func(news):
        return news["visit_time"] if "visit_time" in news else "1970-01-01T08:00:00Z"
    favorites_list.sort(key=key_func, reverse=True)
    return favorites_list


def remove_favorites(user: UserBasicInfo, news_id):
    """
        remove a news from user's favorites
    """
    if not user.favorites:
        user.favorites = {}
        return False
    if str(news_id) in user.favorites:

        try:
            LOCAL_NEWS_MANAGER.del_local_news(int(news_id))
        except Exception as error:
            print(error)

        user.favorites.pop(str(news_id))
        user.full_clean()
        user.save()
        return True
    return False


def clear_favorites(user: UserBasicInfo):
    """
        remove all news from user's favorites
    """
    if user.favorites:
        for news_id in user.favorites:
            try:
                LOCAL_NEWS_MANAGER.del_local_news(int(news_id))
            except Exception as error:
                print(error)
    user.favorites = {}
    user.full_clean()
    user.save()


def user_favorites_pages(user: UserBasicInfo, page: int):
    """
        favorites pages for user
        page start from 0
    """
    if not user.favorites:
        return [], 0
    favorites_page = []
    begin = page * FAVORITES_PRE_PAGE
    end = (page + 1) * FAVORITES_PRE_PAGE
    favorites_list = get_favorites(user)
    favorites_page = favorites_list[begin:end]

    user_favorites_dict = get_user_favorites_dict(user=user)
    user_readlist_dict = get_user_readlist_dict(user=user)

    for news in favorites_page:
        try:
            ai_news = LOCAL_NEWS_MANAGER.get_one_ai_news(news["id"])
            if "summary" in ai_news:
                news["summary"] = ai_news["summary"]
            else:
                news["summary"] = ""
        except Exception as error:
            print(error)

    for news in favorites_page:
        news["is_favorite"] = in_favorite_check(user_favorites_dict, int(news["id"]))
        news["is_readlater"] = in_readlist_check(user_readlist_dict, int(news["id"]))

    return favorites_page, math.ceil(len(favorites_list) / FAVORITES_PRE_PAGE)


def resize_image(image, size=(512, 512)):
    """
        cut image
    """
    img = Image.open(image)
    cropped_image = img.resize(size, Image.ANTIALIAS)
    return cropped_image


def pil_to_base64(image):
    """
        transfer pil image to base64
    """
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    byte_data = buffer.getvalue()
    return base64.b64encode(byte_data).decode()


def connect_to_db(configure):
    """
    {
        "hostname": "43.143.201.186",
        "port": 5432,
        "username": "webread",
        "password": "asyNcwebRead",
        "database": "web"
    }
    """
    connection = psycopg2.connect(
        database=configure["database"],
        user=configure["username"],
        password=configure["password"],
        host=configure["hostname"],
        port=str(configure["port"])
    )
    return connection


def return_user_info(user: UserBasicInfo, user_token="", start_time=None):
    """
        return user info
    """
    try:
        user_tags = []
        if user.tags:
            user_tags_dict = user.tags
            for key_value in sorted(
                user_tags_dict.items(),
                key=lambda kv:(kv[1], kv[0]),
                reverse=True
            )[:MAX_RETURN_USER_TAG]:
                user_tags.append({"key": key_value[0], "value": key_value[1]})
                # user_tags[key_value[0]] = key_value[1]
        else:
            user.tags = {}
            user.full_clean()
            user.save()

        user_avatar = user.avatar
        if not user_avatar:
            with open("data/default_avatar.base64", "r", encoding="utf-8") as avatar_file:
                user_avatar = avatar_file.read()

        status_code = 200
        response_msg = {
            "data": {
                "id": user.id,
                "user_name": user.user_name,
                "signature": user.signature,
                "tags": user_tags,
                "mail": user.mail,
                "avatar": user_avatar,
                "register_date": user.register_date,
            },
            "code": 0,
            "message": "SUCCESS",
        }
        if user_token:
            response_msg["data"]["token"] = user_token
        if start_time:
            response_msg["time"] = time.time() - start_time
        return JsonResponse(
            data=response_msg,
            status=status_code,
            headers={'Access-Control-Allow-Origin':'*'}
        )

    except Exception as internal_error:
        print(internal_error)
        return internal_error_response(error=str(internal_error))


def get_data_from_db(connection, select="*", filter_command="", order_command="", limit=200):
    """
        get data from db
    """
    element_names = select
    if isinstance(select, list):
        select = ",".join(select)
    cursor = connection.cursor()
    if filter_command:
        filter_command = "WHERE " + filter_command
    cursor.execute("SELECT {select} FROM news {filter_command} {order} LIMIT {limit}".format(
        select=select,
        filter_command=filter_command,
        order=order_command,
        limit=str(limit)
    ))
    rows = cursor.fetchall()
    results = []
    for row in rows:
        if isinstance(element_names, str):
            element_names = list(range(len(row)))
        result = {}
        for i in range(len(element_names)):
            result[element_names[i]] = row[i]
        results.append(result)
    return results


def close_db_connection(connection):
    """
        close db connection
    """
    connection.close()


# return md5 of a string
def md5(string):
    """
        input: str
        output: md5(str)
    """
    md5_calculator = hashlib.md5()
    md5_calculator.update(string.encode(encoding='UTF-8'))
    return str(md5_calculator.hexdigest())


def create_token(user_name, user_id=0):
    """
        create a jwt token for a user
    """
    encoded_token = "Bearer " + jwt.encode(
        {
            "id":user_id,
            "user_name": user_name,
            "EXPIRE_TIME": time.time() + EXPIRE_TIME
        },
        SECRET_KEY,
        algorithm="HS256"
    )
    return encoded_token


def decode_token(encoded_token):
    """
        decode a jwt token
    """
    return jwt.decode(
        encoded_token.replace("Bearer ",""),
        SECRET_KEY,
        algorithms=["HS256"]
    )


def token_expired(token):
    """
        check if the token is expired
    """
    if token["EXPIRE_TIME"] < time.time():
        return True
    return False


def add_token_to_white_list(encoded_token):
    """
        add user's token to white list
    """
    decoded_token = decode_token(encoded_token)
    user_id = decoded_token["id"]
    if user_id not in TOKEN_WHITE_LIST:
        TOKEN_WHITE_LIST[user_id] = []
    while len(TOKEN_WHITE_LIST[user_id]):  # pop all expired token
        if token_expired(decode_token(TOKEN_WHITE_LIST[user_id][0])):
            TOKEN_WHITE_LIST[user_id].pop(0)
        else:
            break
    if encoded_token not in TOKEN_WHITE_LIST[user_id]:
        TOKEN_WHITE_LIST[user_id].append(encoded_token)


def check_token_in_white_list(encoded_token):
    """
        check user's token in white list
    """
    decoded_token = decode_token(encoded_token)
    user_id = decoded_token["id"]
    if user_id not in TOKEN_WHITE_LIST:
        return False
    while len(TOKEN_WHITE_LIST[user_id]):  # pop all expired token
        if token_expired(decode_token(TOKEN_WHITE_LIST[user_id][0])):
            TOKEN_WHITE_LIST[user_id].pop(0)
        else:
            break
    if encoded_token in TOKEN_WHITE_LIST[user_id]:
        return True
    return False


def del_token_from_white_list(encoded_token):
    """
        del token from white list, used when logout.
        return true if succeed.
    """
    decoded_token = decode_token(encoded_token)
    user_id = decoded_token["id"]
    if user_id not in TOKEN_WHITE_LIST:
        return False
    while len(TOKEN_WHITE_LIST[user_id]):  # pop all expired token
        if token_expired(decode_token(TOKEN_WHITE_LIST[user_id][0])):
            TOKEN_WHITE_LIST[user_id].pop(0)
        else:
            break
    if encoded_token in TOKEN_WHITE_LIST[user_id]:
        while encoded_token in TOKEN_WHITE_LIST[user_id]:  # normally only loop once
            TOKEN_WHITE_LIST[user_id].remove(encoded_token)
        return True
    return False


def del_all_token_of_an_user(user_id):
    """
        del all token of an user from white list.
    """
    if user_id in TOKEN_WHITE_LIST:
        TOKEN_WHITE_LIST[user_id] = []


with open("config/config.json","r",encoding="utf-8") as config_file:
    config = json.load(config_file)
CRAWLER_DB_CONNECTION = connect_to_db(config["crawler-db"])

NEWS_CACHE = NewsCache(
    db_connection=CRAWLER_DB_CONNECTION
)

DB_SCANNER = DBScanner(
    db_connection=CRAWLER_DB_CONNECTION,
    news_cache=NEWS_CACHE,
    get_data_from_db=get_data_from_db,
    testing_mode=TESTING_MODE,
    front_page_news_num=FRONT_PAGE_NEWS_NUM,
    db_check_interval=DB_CHECK_INTERVAL,
    db_news_look_back=DB_NEWS_LOOK_BACK,
    db_update_minimum_interval=DB_UPDATE_MINIMUM_INTERVAL
)

THREAD_POOL = threadpool.ThreadPool(1)

LOCAL_NEWS_MANAGER = LocalNewsManager()


def start_db_scanner(thread_id):
    """
        start db scanner
    """
    print("Start db scanner", thread_id)
    DB_SCANNER.run()


for REQUEST in threadpool.makeRequests(start_db_scanner, [0]):
    THREAD_POOL.putRequest(REQUEST)

try:
    with open("config/lucene.json","r",encoding="utf-8") as config_file:
        config = json.load(config_file)
    rpc_client = RPCClient(
        JSONRPCProtocol(),
        HttpPostClientTransport('http://' + config['url'] + ':' + str(config['port']))
    )
    SEARCH_CONNECTION = rpc_client.get_proxy()
except Exception as error:
    print(error)
