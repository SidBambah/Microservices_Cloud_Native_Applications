import json
import logging
import os
import requests
import boto3
logger = logging.getLogger()
logger.setLevel(logging.INFO)

global table
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AddressTable')


def update_database(address):
    global table
    
    table.put_item(
       Item={
            'address_id': address["delivery_point_barcode"],
            'primary_number': address["components"]["primary_number"],
            'street_name': address["components"]["street_name"],
            'street_suffix': address["components"]["street_suffix"],
            'city_name': address["components"]["city_name"],
            'state': address["components"]["state_abbreviation"],
            'zipcode': address["components"]["zipcode"]
        }
)

    pass
    

def verify_address(inputs):
    auth_id = os.environ['auth_id']
    auth_token = os.environ['auth_token']
    
    logger.info("Inputs")
    if ('street' in inputs) & ('city' in inputs) & ('state' in inputs):
        street = inputs['street'].replace(" ", "+")
        city = inputs['city'].replace(" ", "+")
        state = inputs['state'].replace(" ", "+")
        url = "https://us-street.api.smartystreets.com/street-address?" + "auth-id=" + \
        auth_id + "&auth-token=" + auth_token + "&street=" + street + \
        "&city=" + city + "&state=" + state
        
        r = requests.get(url)
        if r.text:
            update_database(r.json()[0])
            return r.json()[0]["delivery_point_barcode"]
        else:
            return False
    else:
        return False

def get_address(address_id):
    global table
    
    if 'address-id' in address_id:
        response = table.get_item(
            Key={
                'address_id': address_id['address-id']
            }
        )
        item = response['Item']
        if item:
            return item
        else:
            return False
    else:
        return False

def lambda_handler(event, context):
    if event.get("httpMethod", None) == "GET":
        inputs = event.get("pathParameters")
        item = get_address(inputs)
        if item:
            return {
                'statusCode': 200,
                'body': json.dumps(item)
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Address not found')
            }
        
    elif event.get("httpMethod", None) == "POST":
        inputs = json.loads(event.get("body", None))
        address_id = verify_address(inputs)
        if address_id:
            return {
                'statusCode': 201,
                'body': json.dumps(address_id),
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Address not valid')
            }
    else:
        return {
            'statusCode': 501,
            'body': json.dumps('Method not IMPLEMENTED')
        }