from Middleware.security import authorize
from Context.Context import Context
import jwt 

def t1():
    encoded = jwt.encode({"Authorization": "NYC Auth Header"}, "NYC Secret Code", algorithm="HS256")
    print(authorize(encoded))

def t2():
    encoded = jwt.encode({"Authorization": "INCORRECT CODE"}, "NYC Secret Code", algorithm="HS256")
    print(authorize(encoded))

#t1()
#t2()