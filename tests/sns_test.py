from Middleware.notification import publish_it as publish
import json

def t1():
    message = {"customers_email":"sids53@gmail.com"}
    publish(message)
t1()