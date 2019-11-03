
import requests
import json

def t1():
    # Get address id from SmartyStreets
    AddressServiceEndpoint = 'https://2bdd302ncj.execute-api.us-east-1.amazonaws.com/dev/AddressService'

    address = {
        "state": "CA",
        "city": "Mountain View",
        "street": "1600 Amphitheatre Parkway"
    }

    x = requests.post(AddressServiceEndpoint, data = json.dumps(address))
    print(x.status_code)
    if x.status_code != 201:
        print("Bad Address")
    else:
        print(x.text)
        
t1()