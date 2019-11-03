import requests
import json

def verify_address(address):

    # Get address id from SmartyStreets
    AddressServiceEndpoint = 'https://2bdd302ncj.execute-api.us-east-1.amazonaws.com/dev/AddressService'

    required = {"state", "city", "street"}
    address = { key: address[key] for key in required }

    rsp = requests.post(AddressServiceEndpoint, data = json.dumps(address))

    if rsp.status_code != 201:
        return None
    else:
        return rsp.json()