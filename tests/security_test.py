from Middleware.security import authorize
from Context.Context import Context
import jwt 

def t1():
    encoded = jwt.encode({"Authorization": "NYC Auth Header", "email": "admin@columbia.edu"}, "NYC Secret Code", algorithm="HS256")
    print(encoded)

def t2():
    encoded = jwt.encode({"Authorization": "INCORRECT CODE"}, "NYC Secret Code", algorithm="HS256")
    print(encoded)

t1()
#t2()