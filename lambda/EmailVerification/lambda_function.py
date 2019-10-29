import json
import logging
import json
import jwt
import requests
import boto3
from botocore.exceptions import ClientError
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Endpoint where flask application is running
FLASK_ENDPOINT = "http://flask-env2.us-east-1.elasticbeanstalk.com"

# This address must be verified with Amazon SES.
SENDER = "E6156 Test <sids53@gmail.com>"

# Specify a configuration set. If you do not want to use a configuration
# set, comment the following variable, and the 
# ConfigurationSetName=CONFIGURATION_SET argument below.
CONFIGURATION_SET = "ConfigSet"

# If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
AWS_REGION = "us-east-1"

# The subject line for the email.
SUBJECT = "User Registration Verification"

# The email body for recipients with non-HTML email clients.
BODY_TEXT = ("Amazon SES Test (Python)\r\n"
             "This email was sent with Amazon SES using the "
             "AWS SDK for Python (Boto)."
            )

#Verification link to be generated later
VERIFICATION_LINK = ""

# The HTML body of the email.
BODY_HTML = "" 

#Cloud Gateway API endpoint
API_ENDPOINT = "https://2bdd302ncj.execute-api.us-east-1.amazonaws.com/dev/EmailVerification/"

# The character encoding for the email.
CHARSET = "UTF-8"

# Create a new SES resource and specify a region.
client = boto3.client('ses',region_name=AWS_REGION)

# Create the email verification link with JWT
def gen_link(em):
    global VERIFICATION_LINK, BODY_HTML
    encoded = jwt.encode({"email": em}, "NYC Secret Code", algorithm="HS256")
    token = str(encoded, 'utf-8')
    VERIFICATION_LINK = API_ENDPOINT + "?token=" + token
    BODY_HTML = """<html>
                <head></head>
                <body>
                  <h1>Amazon SES Test (SDK for Python)</h1>
                  <p>This email was sent with
                    <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
                    <a href='https://aws.amazon.com/sdk-for-python/'>
                      AWS SDK for Python (Boto)</a>.</p>
                      <form action="www.google.com">
                        <input type="submit" value="Go to Google" />
                    </form>
                    <p>Click this <a href= """ + VERIFICATION_LINK + """> link </a>
                    to verify new user.</p>
                </body>
                </html>
            """
    logger.info(VERIFICATION_LINK)
# Try to send the email.
def send_email(em):
    try:
        print("em = ", em)
        # Generate verification link
        gen_link(em)
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    em
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
               Source=SENDER
            # If you are not using a configuration set, comment or delete the
            # following line
            #ConfigurationSetName=CONFIGURATION_SET,
            )
    # Display an error if something goes wrong. 
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


def handle_sns_event(records):

    sns_event = records[0]['Sns']
    topic_arn = sns_event.get("TopicArn", None)
    topic_subject = sns_event.get("Subject", None)
    topic_msg = sns_event.get("Message", None)

    print("SNS Subject = ", topic_subject)
    if topic_msg:
        json_msg = None
        try:
            json_msg = json.loads(topic_msg)
            print("Message = ", json.dumps(json_msg, indent=2))
        except:
            print("Could not parse message.")
        em = json_msg["user_email"]
        send_email(em)

# Check if verification link is correct
def check_click(query):
    logger.info(query)
    if query:
        if 'token' in query:
            verifiedUser = jwt.decode(query['token'], "NYC Secret Code", algorithm="HS256")
            if verifiedUser['email']:
                return verifiedUser
        else:
            return False
    else:
        return False
    
# Send verified user to flask application
def send_flask(user):
    auth = jwt.encode({"Authorization": "NYC Auth Header"}, \
    "NYC Secret Code", algorithm="HS256").decode('utf-8')
    body = {"email": user['email'], "status": "ACTIVE"}
    header = {'Content-Type': 'application/json', "Authorization": auth}
    # Send user variable directly, add new data to body
    logger.info(header)
    res = requests.put(FLASK_ENDPOINT + '/api/user/' + user['email'], \
    data = json.dumps(body), \
    headers = header)
    return True
    
def lambda_handler(event, context):
    
    logger.info(event)
    if event.get("Records", None):
        logger.info('Received SNS Event')
        handle_sns_event(event.get("Records",None))
        return {
                'statusCode': 404,
                'body': json.dumps('Verification Email Sent')
            }
    elif event.get("path", None):
        logger.info('Received Email Verification Click')
        rsp = check_click(event.get("queryStringParameters"))
        if rsp:
            #Send to Beanstalk application here
            if send_flask(rsp):
                return {
                    'statusCode': 302,
                    'headers': {'Location': 'http://www.google.com'},
                    'body': json.dumps('Email Verified')
                }
            else:
                return {
                    'statusCode': 404,
                    'body': json.dumps('Could not verify user')
                }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Email not Verified')
            }
    else:
        return {
                'statusCode': 404,
                'body': json.dumps('Improper event')
            }