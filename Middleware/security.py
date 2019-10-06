import jwt

def check_auth(auth):
    auth = jwt.decode(auth, "NYC Secret Code", algorithm="HS256")
    if "Authorization" in auth.keys():
        return auth["Authorization"] == "NYC Auth Header"
    else:
        return False