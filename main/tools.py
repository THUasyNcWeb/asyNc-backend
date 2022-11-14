"""
This .py file contains most commenly used tools in views.py

Created by sxx
"""
import hashlib
import time
import base64
import json
import re
from io import BytesIO

import jwt
import psycopg2
from PIL import Image
from django.http import JsonResponse
from .models import UserBasicInfo
from .responses import internal_error_response

EXPIRE_TIME = 7 * 86400  # 30s for testing. 7 days for deploy.
SECRET_KEY = "A good coder is all you need."

TOKEN_WHITE_LIST = {}  # storage alive token for each user

CATEGORY_LIST = [
    "",
    "ent",
    "sports",
    "mil",
    "politics",
    "tech",
    "social",
    "finance",
    "auto",
    "game",
    "women",
    "health",
    "history",
    "edu"
]

CATEGORY_FRONT_TO_BACKEND = {
    "": "",
    "home": "",
    "sport": "sports",
    "fashion": "women",
    "ent": "ent",
    "sports": "sports",
    "mil": "mil",
    "politics": "politics",
    "tech": "tech",
    "social": "social",
    "finance": "finance",
    "auto": "auto",
    "game": "game",
    "women": "women",
    "health": "health",
    "history": "history",
    "edu": "edu",
}

CRAWLER_DB_CONNECTION = None

FAVORITES_PRE_PAGE = 10


def in_favorite_check(favorites: dict, news_id: int):
    """
        check if in favorites list
    """
    if news_id in favorites:
        return True
    return False


def get_user_favorites(user: UserBasicInfo):
    """
        get user favorites dict
    """
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


def add_to_read_history(user: UserBasicInfo, news: dict):
    """
        add a news to user's read history
    """
    if "id" not in news:
        return
    if not user.read_history:
        user.read_history = {}
    user.read_history[str(news["id"])] = news
    user.full_clean()
    user.save()


def get_read_history(user: UserBasicInfo):
    """
        get read history list from a user
    """
    if not user.read_history:
        user.read_history = {}
    return list(user.read_history.values())


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
    return read_history_page, len(read_history_list)


def add_to_readlist(user: UserBasicInfo, news: dict):
    """
        add a news to user's readlist
    """
    if "id" not in news:
        return
    if not user.readlist:
        user.readlist = {}
    user.readlist[str(news["id"])] = news
    user.full_clean()
    user.save()


def get_readlist(user: UserBasicInfo):
    """
        get readlist list from a user
    """
    if not user.readlist:
        user.readlist = {}
    return list(user.readlist.values())


def remove_readlist(user: UserBasicInfo, news_id):
    """
        remove a news from user's readlist
    """
    if not user.readlist:
        user.readlist = {}
        return False
    if str(news_id) in user.readlist:
        user.readlist.pop(str(news_id))
        user.full_clean()
        user.save()
        return True
    return False


def clear_readlist(user: UserBasicInfo):
    """
        remove all news from user's readlist
    """
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
    return readlist_page, len(readlist_list)


def add_to_favorites(user: UserBasicInfo, news: dict):
    """
        add a news to user's favorites
    """
    if "id" not in news:
        return
    if not user.favorites:
        user.favorites = {}
    user.favorites[str(news["id"])] = news
    user.full_clean()
    user.save()


def get_favorites(user: UserBasicInfo):
    """
        get favorites list from a user
    """
    if not user.favorites:
        user.favorites = {}
    return list(user.favorites.values())


def remove_favorites(user: UserBasicInfo, news_id):
    """
        remove a news from user's favorites
    """
    if not user.favorites:
        user.favorites = {}
        return False
    if str(news_id) in user.favorites:
        user.favorites.pop(str(news_id))
        user.full_clean()
        user.save()
        return True
    return False


def clear_favorites(user: UserBasicInfo):
    """
        remove all news from user's favorites
    """
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
    return favorites_page, len(favorites_list)


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


def return_user_info(user, user_token=""):
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
            ):
                user_tags.append(key_value[0])

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
                "tags": user_tags[:10],
                "mail": user.mail,
                "avatar": user_avatar,
            },
            "code": 0,
            "message": "SUCCESS",
        }
        if user_token:
            response_msg["data"]["token"] = user_token

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
