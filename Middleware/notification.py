import boto3
import json


def publish_it(msg):

    client = boto3.client('sns')
    txt_msg = json.dumps(msg)
    client.publish(TopicArn="arn:aws:sns:us-east-1:836570052658:UserChange", Subject="User Change",
                   Message=txt_msg)