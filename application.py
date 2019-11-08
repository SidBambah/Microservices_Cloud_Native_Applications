
# Import functions and objects the microservice needs.
# - Flask is the top-level application. You implement the application by adding methods to it.
# - Response enables creating well-formed HTTP/REST responses.
# - requests enables accessing the elements of an incoming HTTP/REST request.
#
from flask import Flask, Response, request
from flask_cors import CORS
from datetime import datetime
import json
import uuid

from Services.CustomerInfo.Users import UsersService as UserService
from Services.CustomerProfile.Profiles import ProfileService
from Services.RegisterLogin.RegisterLogin import RegisterLoginSvc
from Context.Context import Context
from Middleware import notification
from Middleware import security
from Middleware import etags
from Middleware import address_service_connection
# Setup and use the simple, common Python logging framework. Send log messages to the console.
# The application should get the log level out of the context. We will change later.
#
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

###################################################################################################################
#
# AWS put most of this in the default application template.
#
# AWS puts this function in the default started application
# print a nice greeting.
def say_hello(username = "World"):
    return '<p>Hello %s!</p>\n' % username

# AWS put this here.
# some bits of text for the page.
header_text = '''
    <html>\n<head> <title>EB Flask Test</title> </head>\n<body>'''
instructions = '''
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'

# EB looks for an 'application' callable by default.
# This is the top-level application that receives and routes requests.
application = Flask(__name__)
CORS(application)
# add a rule for the index page. (Put here by AWS in the sample)
application.add_url_rule('/', 'index', (lambda: header_text +
    say_hello() + instructions + footer_text))

# add a rule when the page is accessed with a name appended to the site
# URL. Put here by AWS in the sample
application.add_url_rule('/<username>', 'hello', (lambda username:
    header_text + say_hello(username) + home_link + footer_text))

##################################################################################################################
# The stuff I added begins here.

_default_context = None
_user_service = None
_registration_service = None
_profile_service = None

def _get_default_context():

    global _default_context

    if _default_context is None:
        _default_context = Context.get_default_context()

    return _default_context


def _get_user_service():
    global _user_service

    if _user_service is None:
        _user_service = UserService(_get_default_context())

    return _user_service

def _get_profile_service():
    global _profile_service

    if _profile_service is None:
        _profile_service = ProfileService(_get_default_context())

    return _profile_service

def _get_registration_service():
    global _registration_service

    if _registration_service is None:
        _registration_service = RegisterLoginSvc()

    return _registration_service

def init():

    global _default_context, _user_service, _profile_service

    _default_context = Context.get_default_context()
    _user_service = UserService(_default_context)
    _profile_service = ProfileService(_default_context)
    logger.debug("_user_service = " + str(_user_service))


# 1. Extract the input information from the requests object.
# 2. Log the information
# 3. Return extracted information.
#
def log_and_extract_input(method, path_params=None):

    path = request.path
    args = dict(request.args)
    data = None
    headers = dict(request.headers)
    method = request.method

    try:
        if request.data is not None:
            data = request.json
        else:
            data = None
    except Exception as e:
        # This would fail the request in a more real solution.
        log_msg = "Log and Extract: Exception = " + str(e)
        logger.error(log_msg)
        data = "You sent something but I could not get JSON out of it."

    log_message = str(datetime.now()) + ": Method " + method

    inputs =  {
        "path": path,
        "method": method,
        "path_params": path_params,
        "query_params": args,
        "headers": headers,
        "body": data
        }

    log_message += " received: \n" + json.dumps(inputs, indent=2)
    logger.debug(log_message)

    return inputs

def log_response(method, status, data, txt):

    msg = {
        "method": method,
        "status": status,
        "txt": txt,
        "data": data
    }

    logger.debug(str(datetime.now()) + ": \n" + json.dumps(msg, indent=2))


# This function performs a basic health check. We will flesh this out.
@application.route("/health", methods=["GET"])
def health_check():

    rsp_data = { "status": "healthy", "time": str(datetime.now()) }
    rsp_str = json.dumps(rsp_data)
    rsp = Response(rsp_str, status=200, content_type="application/json")
    return rsp


@application.route("/demo/<parameter>", methods=["GET", "POST"])
def demo(parameter):

    inputs = log_and_extract_input(demo, { "parameter": parameter })

    msg = {
        "/demo received the following inputs" : inputs
    }

    rsp = Response(json.dumps(msg), status=200, content_type="application/json")
    return rsp

# Middleware before PUT and DELETE requests
@application.before_request
def before_request():
    inputs = log_and_extract_input(demo)
    rsp = security.authorize(inputs)
    if rsp is not None:
        rsp_status = 404
        rsp_txt = "Not authorized"
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")
        return full_rsp
    else:
        pass

@application.route("/api/users", methods=["GET"])
def get_users():
    
    global _user_service
    inputs = log_and_extract_input(demo)
    rsp_data = None
    rsp_status = None
    rsp_txt = None

    try:

        user_service = _get_user_service()
        
        query_params = json.dumps(inputs["query_params"])

        rsp = user_service.get_users(query_params)
        
        if rsp is not None:
            rsp_data = rsp
            rsp_status = 200
            rsp_txt = "OK"
        else:
            rsp_data = None
            rsp_status = 404
            rsp_txt = "NOT FOUND"

        if rsp_data is not None:
            full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")
    except Exception as e:
        log_msg = "/users: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/users", rsp_status, rsp_data, rsp_txt)

    return full_rsp

@application.route("/api/user/<email>", methods=["GET", "PUT", "DELETE"])
def user_email(email):

    global _user_service

    inputs = log_and_extract_input(demo, { "parameters": email })
    rsp_data = None
    rsp_status = None
    rsp_txt = None
    headers = None

    try:

        user_service = _get_user_service()

        if inputs["method"] == "GET":

            rsp = user_service.get_by_email(email)

            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
                headers = {"ETag": etags.generate_etag(rsp)}
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"
        elif inputs["method"] == "PUT":
            usr_info = inputs["body"]
            if "email" not in usr_info:
                usr_info["email"] = email

            old_etag = request.headers.get('If-None-Match', '')
            
            if etags.check_etag(old_etag, user_service.get_by_email(email)):
                rsp = user_service.update_user(usr_info)
            else:
                rsp = "Bad ETag"

            if (rsp == "Bad ETag"):
                rsp_data = None
                rsp_status = 304
                rsp_txt = rsp
            elif rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "UPDATED"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT UPDATED"
        elif inputs["method"] == "DELETE":
            rsp = user_service.delete_user(email)
            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT DELETED"
        else:
            rsp_data = None
            rsp_status = 501
            rsp_txt = "NOT IMPLEMENTED"

        if rsp_data is not None:
            if headers is not None:
                full_rsp = Response(json.dumps(rsp_data), status=rsp_status, headers=headers, content_type="application/json")
            else:
                full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/email: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/email", rsp_status, rsp_data, rsp_txt)

    return full_rsp

@application.route("/api/registrations", methods=["POST"])
def user_registration():

    inputs = log_and_extract_input(demo)
    rsp_data = None
    rsp_status = None
    rsp_txt = None

    try:

        r_svc = _get_registration_service()

        if inputs["method"] == "POST":
            #Get the user's information from the POST request
            user_data = inputs["body"]
            #Set default status to pending and generate random id
            user_data['status'] = "PENDING"
            user_data['id'] = str(uuid.uuid4())
            rsp = r_svc.register(user_data)

            if rsp is not None:
                #Send user verification email
                notification.publish_it({"user_email": user_data['email']})
                rsp_data = rsp
                rsp_status = 201
                rsp_txt = "OK"
                link = rsp[0]
                auth = rsp[1]
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "COULD NOT CREATE"
        else:
            rsp_data = None
            rsp_status = 501
            rsp_txt = "Only POST Method Allowed"

        if rsp_data is not None:
            headers = {"Location": "/api/users/" + link}
            headers["Authorization"] =  auth
            full_rsp = Response(json.dumps(rsp_data), status=rsp_status, headers=headers, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/registrations: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/registrations", rsp_status, rsp_data, rsp_txt)

    return full_rsp

@application.route("/api/login", methods=["POST"])
def login():

    inputs = log_and_extract_input(demo, {"parameters": None})
    rsp_data = None
    rsp_status = None
    rsp_txt = None

    try:

        r_svc = _get_registration_service()

        if inputs["method"] == "POST":

            rsp = r_svc.login(inputs['body'])

            if rsp is not None:
                rsp_data = "OK"
                rsp_status = 201
                rsp_txt = "CREATED"
            else:
                rsp_data = None
                rsp_status = 403
                rsp_txt = "NOT AUTHORIZED"
        else:
            rsp_data = None
            rsp_status = 501
            rsp_txt = "NOT IMPLEMENTED"

        if rsp_data is not None:
            # TODO Generalize generating links
            headers = {"Authorization": rsp}
            headers["Access-Control-Expose-Headers"] = "Authorization"
            full_rsp = Response(json.dumps(rsp_data, default=str), headers=headers,
                                status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/api/registration: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/api/registration", rsp_status, rsp_data, rsp_txt)

    return full_rsp

@application.route("/api/profile", methods=["POST", "GET", "PUT", "DELETE"])
def profile():
    global _profile_service
    global _user_service

    inputs = log_and_extract_input(demo, {"parameters": None})
    rsp_data = None
    rsp_status = None
    rsp_txt = None
    headers= None

    try:
        profile_service = _get_profile_service()
        user_service = _get_user_service()

        if inputs["method"] == "GET":
            query_params = json.dumps(inputs["query_params"])

            rsp = profile_service.get_profile_entries(query_params)
        
            if rsp is not None:
                if len(rsp) > 0:
                    entries = []
                    for entry in rsp:
                        entries.append({'element_id': entry['element_id'], 'element_type': entry['element_type'], 'element_subtype': entry['element_subtype'],
                                        'element_value': entry['element_value']})
                    temp_rsp = rsp
                    rsp = {}
                    rsp['userid'] = temp_rsp[0]['userid']
                    rsp['profileid'] = temp_rsp[0]['profileid']
                    rsp['entries'] = entries
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"
        elif inputs["method"] == "POST":
            #Get the profile entry information from the POST request
            profile_data = inputs["body"]
            #Get user id from provided email
            user_info = user_service.get_by_email(profile_data["email"])
            if user_info is None:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "User not found with that email"
            else:
                profile_data['userid'] = user_info["id"]
                #User ID and Profile ID are the same for simplicity
                profile_data['profileid'] = profile_data['userid']

                #Processing if it is an address
                if profile_data["element_type"] == "ADDRESS":
                    address_id = address_service_connection.verify_address(profile_data)
                    if address_id is not None:
                        profile_data["element_value"] = "/address/" + address_id
                        rsp = profile_service.create_profile_entry(profile_data)
                else:
                    rsp = profile_service.create_profile_entry(profile_data)
                if rsp is not None:
                    rsp_data = rsp
                    rsp_status = 201
                    rsp_txt = "Entry Created"
                else:
                    rsp_data = None
                    rsp_status = 404
                    rsp_txt = "Entry Not Created"
        elif inputs["method"] == "PUT":
            profile_data = inputs["body"]
            #Get user id from provided email
            user_info = user_service.get_by_email(profile_data["email"])
            if user_info is None:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "User not found with that email"
            else:
                profile_data['userid'] = user_info["id"]
                profile_data['profileid'] = profile_data['userid']

                #Processing if it is an address
                if profile_data["element_type"] == "ADDRESS":
                    address_id = address_service_connection.verify_address(profile_data)
                    if address_id is not None:
                        profile_data["element_value"] = "/address/" + address_id
                        rsp = profile_service.update_profile_entry(profile_data)
                else:
                    rsp = profile_service.update_profile_entry(profile_data)

                if rsp is not None:
                    rsp_data = rsp
                    rsp_status = 200
                    rsp_txt = "UPDATED"
                else:
                    rsp_data = None
                    rsp_status = 404
                    rsp_txt = "NOT UPDATED"
        elif inputs["method"] == "DELETE":
            #Get the profile entry information from the DELETE request
            entry_info = inputs["body"]
            #Get user id from provided email
            user_info = user_service.get_by_email(entry_info["email"])
            if user_info is None:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "User not found with that email"
            else:
                entry_info['userid'] = user_info["id"]
                rsp = profile_service.delete_profile_entry(entry_info)
                if rsp is not None:
                    rsp_data = rsp
                    rsp_status = 200
                    rsp_txt = "Entry Deleted"
                else:
                    rsp_data = None
                    rsp_status = 404
                    rsp_txt = "Entry Not Deleted"
        else:
            rsp_data = None
            rsp_status = 501
            rsp_txt = "NOT IMPLEMENTED"
        
        if rsp_data is not None:
            if headers is not None:
                full_rsp = Response(json.dumps(rsp_data), status=rsp_status, headers=headers, content_type="application/json")
            else:
                full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/api/profile: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/api/profile", rsp_status, rsp_data, rsp_txt)

    return full_rsp



logger.debug("__name__ = " + str(__name__))
# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.

    logger.debug("Starting Project EB at time: " + str(datetime.now()))
    init()

    application.debug = True
    application.run()