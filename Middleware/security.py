from Context.Context import Context
import jwt
from time import time

_context = Context.get_default_context()

def authorize(url, method, token):
    token = jwt.decode(token, key=_context.get_context("JWT_SECRET"), algorithm="HS256")
    if "Authorization" in token.keys():
        if token["Authorization"] == "NYC Auth Header":
            print(method)
            if (method == "DELETE") & (token["email"] == "admin@columbia.edu"):
                return True
            elif (method == "PUT") & (token["email"] == url.split('/')[-1]):
                return True
            else:
                return False
        else:
            return False
    return False


def hash_password(pwd):
    global _context
    h = jwt.encode(pwd, key=_context.get_context("JWT_SECRET"), algorithm="HS256")
    h = str(h)
    return h

def generate_token(info):

    info["timestamp"] =  time()
    info["Authorization"] = "NYC Auth Header"

    h = jwt.encode(info, key=_context.get_context("JWT_SECRET"))
    h = str(h)

    return h