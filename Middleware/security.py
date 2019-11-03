from Context.Context import Context
import jwt
from time import time

_context = Context.get_default_context()

def check_token(token, method, url):
    token = jwt.decode(token, key=_context.get_context("JWT_SECRET"), algorithm="HS256")
    if "Authorization" in token.keys():
        if token["Authorization"] == "NYC Auth Header":
            if (method == "DELETE") & (token["email"] == "admin@columbia.edu"):
                return True
            elif (method == "PUT") & (token["email"] == url.split('/')[-1]):
                return True
            else:
                return False
        else:
            return False
    else:
        return False

def authorize(inputs):
    method = inputs['method']
    url = inputs['path']
    if url.startswith('/api/user'):
        if method == "PUT" or method == "DELETE":
            if "Authorization" in inputs['headers']:
                auth = inputs['headers']["Authorization"]
            else:
                return "Not Authorized"

            if not check_token(auth, method, url):
                return "Not authorized"
            else:
                return None
    return None

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