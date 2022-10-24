"""
This .py file contains most commenly used tools in views.py

Created by sxx
"""
import hashlib
import time
import jwt

EXPIRE_TIME = 7 * 86400  # 30s for testing. 7 days for deploy.
SECRET_KEY = "A good coder is all you need."

TOKEN_WHITE_LIST = {}  # storage alive token for each user


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
    return "Bearer " + jwt.encode(
        {
            "id":user_id,
            "user_name": user_name,
            "EXPIRE_TIME": time.time() + EXPIRE_TIME
        },
        SECRET_KEY,
        algorithm="HS256"
    )


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
