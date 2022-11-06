"""
This .py file contains most commenly used tools in views.py

Created by sxx
"""
import hashlib
import time
import base64
from io import BytesIO

import jwt
import psycopg2
from PIL import Image
from django.http import JsonResponse
from .models import UserBasicInfo, News
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
    "ent": "ent",
    "sport": "sports",
    "tech": "tech",
    "game": "game",
    "fashion": "women",
    "health": "health",
}


def add_to_favorites(user : UserBasicInfo, news : News):
    """
        add a news to user's favorites
    """
    user.favorites.append(news)
    user.full_clean()
    user.save()


def get_favorites(user : UserBasicInfo):
    """
        get favorites list from a user
    """
    return user.favorites


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
