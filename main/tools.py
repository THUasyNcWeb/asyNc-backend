import hashlib

# return md5 of a string
def md5(string):
    """
    input: str
    output: str
    """
    md5_calculator = hashlib.md5()
    md5_calculator.update(string.encode(encoding='UTF-8'))
    return md5_calculator.hexdigest()