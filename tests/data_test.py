
from DataAccess.DataObject import UsersRDB as UsersRDB
import json
from uuid import uuid4

def t1():

    r = UsersRDB.get_by_email('metus.vitae@nibhAliquamornare.edu')
    print("Result = \n", json.dumps(r, indent=2))

def t2():
     usr = {
         "last_name": "Baggins",
         "first_name": "Frodo",
         "id": str(uuid4()),
         "email": "fb@shire.gov",
         "status": "PENDING",
         "password": "goodidea"
     }
     res = UsersRDB.create_user(user_info=usr)
     print("Res = ", res)

def t3():
    r = UsersRDB.delete_user('fb@shire.gov')
    print("Result = \n", json.dumps(r, indent=2))

def t4():
    usr = {
        "last_name": "testupdate",
        "email": "fb@shire.gov",
    }
    res = UsersRDB.update_user(user_info=usr)
    print("Res = ", res)

#t1()
#t2()
#t3()
#t4()