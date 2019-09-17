import threading
from threading import current_thread
import DataAccess.DataAdaptor as data_adaptor
from Context.Context import Context

threadlocal = threading.local()

# We should read this information from the environment.
# Note: Completed
default_connect_info =  {
    "host" :'localhost',
    "user": 'dbuser',
    "password": 'dbuserdbuser',
    "db": "lahman2019raw",
    "charset": 'utf8mb4'
}

## Implemented reading from environment
ctx = Context.get_default_context()
default_connect_info = ctx.get_context("db_connect_info")


def t1():

    current_thread().default_connect_info  = default_connect_info
    data_adaptor._get_default_connection()

t1()