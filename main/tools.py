import hashlib
import jwt
import time

expire_time = 30# 30s for testing. 7 days for deploy.
secret_key = "A good coder is all you need."

# return md5 of a string
def md5(string):
    """
    input: str
    output: str
    """
    md5_calculator = hashlib.md5()
    md5_calculator.update(string.encode(encoding='UTF-8'))
    print(str(md5_calculator.hexdigest()))
    print(str(md5_calculator.hexdigest()))
    return str(md5_calculator.hexdigest())

def create_token(user_name):
    return "Bearer " + jwt.encode({"user_name": user_name, "expire_time": time.time() + expire_time}, secret_key, algorithm="HS256")

def decode_token(encoded_token):
    return jwt.decode(encoded_token.replace("Bearer ",""), secret_key, algorithms=["HS256"])

def token_expired(token):
    if token["expire_time"] < time.time():
        return True
    return False