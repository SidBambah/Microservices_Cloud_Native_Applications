import copy

import os
import json

class Context():

    def __init__(self, inital_ctx=None):

        self._context = inital_ctx


    def get_context(self, ctx_name):

        result = self._context.get(ctx_name, None)
        return result

    def set_context(self, ctx_name, ctx):

        self._context[ctx_name] = copy.deepcopy(ctx)

    @classmethod
    def get_default_context(cls):

        db_connect_info = os.environ.get('db_connect_info', None)
        db_connect_info = json.loads(db_connect_info)
        secret = os.environ.get('JWT_SECRET', None)
        fb_app_token = os.environ.get('FB_APP_TOKEN', None)
        ctx = { "db_connect_info": db_connect_info }
        ctx['JWT_SECRET'] = secret
        ctx['FB_APP_TOKEN'] = fb_app_token
        result = Context(ctx)
        return result