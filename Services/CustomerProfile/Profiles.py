from abc import ABC, abstractmethod
from Context.Context import Context
from DataAccess.DataObject import ProfilesRDB
import json
# The base classes would not be IN the project. They would be in a separate included package.
# They would also do some things.

class ServiceException(Exception):

    unknown_error   =   9001
    missing_field   =   9002
    bad_data        =   9003

    def __init__(self, code=unknown_error, msg="Oh Dear!"):
        self.code = code
        self.msg = msg


class BaseService():

    missing_field   =   2001

    def __init__(self):
        pass


class ProfileService(BaseService):

    required_create_fields = ['last_name', 'first_name', 'email', 'password']

    def __init__(self, ctx=None):

        if ctx is None:
            ctx = Context.get_default_context()

        self._ctx = ctx


    @classmethod
    def get_profile_entries(cls, queryParams):

        result = ProfilesRDB.get_profile_entries(queryParams)
        return result

    @classmethod
    def create_profile_entry(cls, entry_info):
        
        result = ProfilesRDB.create_profile_entry(entry_info)
        return result

    @classmethod
    def update_profile_entry(cls, entry_info):
        
        result = ProfilesRDB.update_profile_entry(entry_info)
        return result

    @classmethod
    def delete_profile_entry(cls, entry_info):

        result = ProfilesRDB.delete_profile_entry(entry_info)
        return result