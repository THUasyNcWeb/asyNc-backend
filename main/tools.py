"""
This .py file contains most commenly used tools in views.py

Created by sxx
"""
import hashlib
import time
import jwt

EXPIRE_TIME = 7 * 86400# 30s for testing. 7 days for deploy.
SECRET_KEY = "A good coder is all you need."

# return md5 of a string
def md5(string):
    """
    input: str
    output: md5(str)
    """
    md5_calculator = hashlib.md5()
    md5_calculator.update(string.encode(encoding='UTF-8'))
    return str(md5_calculator.hexdigest())

def create_token(user_name):
    """
        create a jwt token for a user
    """
    return "Bearer " + jwt.encode({"user_name": user_name,
    "EXPIRE_TIME": time.time() + EXPIRE_TIME}, SECRET_KEY, algorithm="HS256")

def decode_token(encoded_token):
    """
        decode a jwt token
    """
    return jwt.decode(encoded_token.replace("Bearer ",""),
    SECRET_KEY, algorithms=["HS256"])

def token_expired(token):
    """
        check if the token is expired
    """
    if token["EXPIRE_TIME"] < time.time():
        return True
    return False
