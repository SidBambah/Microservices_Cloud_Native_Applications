import DataAccess.DataAdaptor as data_adaptor
from abc import ABC, abstractmethod
import pymysql.err
import json

class DataException(Exception):

    unknown_error   =   1001
    duplicate_key   =   1002

    def __init__(self, code=unknown_error, msg="Something awful happened."):
        self.code = code
        self.msg = msg

class BaseDataObject(ABC):

    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def create_instance(cls, data):
        pass


class UsersRDB(BaseDataObject):

    def __init__(self, ctx):
        super().__init__()

        self._ctx = ctx

    @classmethod
    def get_by_email(cls, email):

        sql = "select * from e6156.users where email=%s"
        res, data = data_adaptor.run_q(sql=sql, args=(email), fetch=True)
        if data is not None and len(data) > 0:
            result =  data[0]
        else:
            result = None

        return result
    
    @classmethod
    def get_users(cls, queryParams):
        queryParams = json.loads(queryParams)
        if "f" in queryParams:
            # Give only selected columns
            f = queryParams["f"].split(',')
            del queryParams["f"]
            sql, args = data_adaptor.create_select("users", queryParams, f)
            res, data = data_adaptor.run_q(sql=sql, args=args, fetch=True)
        else:
            # Give all columns
            sql, args = data_adaptor.create_select("users", queryParams, "*")
            res,data = data_adaptor.run_q(sql=sql, args=args, fetch=True)

        if data is not None:
            result =  data
        else:
            result = None

        return result

    @classmethod
    def create_user(cls, user_info):

        result = None

        try:
            sql, args = data_adaptor.create_insert(table_name="users", row=user_info)
            res, data = data_adaptor.run_q(sql, args)
            if res != 1:
                result = None
            else:
                result = user_info['id']
        except pymysql.err.IntegrityError as ie:
            if ie.args[0] == 1062:
                raise (DataException(DataException.duplicate_key))
            else:
                raise DataException()
        except Exception as e:
            raise DataException()

        return result

    @classmethod
    def update_user(cls, user_info):

        result = None

        try:
            sql, args = data_adaptor.create_update("users", user_info, {"email": user_info['email']})
            res, data = data_adaptor.run_q(sql, args)
            if res != 1:
                result = None
            else:
                result = "Updated successfully"
        except pymysql.err.IntegrityError as ie:
            if ie.args[0] == 1062:
                raise (DataException(DataException.duplicate_key))
            else:
                raise DataException()
        except Exception as e:
            raise DataException()

        return result

    @classmethod
    def delete_user(cls, email):

        sql = "delete from e6156.users where email=%s"
        res, data = data_adaptor.run_q(sql=sql, args=(email), fetch=True)
        if res == 1:
            res = "Successful Deletion"
        else:
            res = None
        return res




