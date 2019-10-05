from Middleware.notification import publish_it as publish
import json

def t1():
    message = {"user_email":"sids53@gmail.com"}
    publish(message)
t1()