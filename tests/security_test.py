from Middleware.security import check_auth as check_auth
import jwt 

def t1():
    encoded = jwt.encode({"Authorization": "NYC Auth Header"}, "NYC Secret Code", algorithm="HS256")
    print(check_auth(encoded))

def t2():
    encoded = jwt.encode({"Authorization": "INCORRECT CODE"}, "NYC Secret Code", algorithm="HS256")
    print(check_auth(encoded))

t1()
t2()