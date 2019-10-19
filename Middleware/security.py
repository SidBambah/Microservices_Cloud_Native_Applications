from Context.Context import Context
import jwt
from time import time

_context = Context.get_default_context()


def authorize(auth):
    auth = jwt.decode(auth, key=_context.get_context("JWT_SECRET"), algorithm="HS256")
    if "Authorization" in auth.keys():
        return auth["Authorization"] == "NYC Auth Header"
    else:
        return False

def hash_password(pwd):
    global _context
    h = jwt.encode(pwd, key=_context.get_context("JWT_SECRET"), algorithm="HS256")
    h = str(h)
    return h

def generate_token(info):

    info["timestamp"] =  time()

    h = jwt.encode(info, key=_context.get_context("JWT_SECRET"))
    h = str(h)

    return h