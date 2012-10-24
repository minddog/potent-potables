import threading
import warnings
import StringIO
import xml.etree.ElementTree as et
from sqlalchemy import exc
from sqlalchemy import event
from sqlalchemy.pool import Pool

from . import configuration

def __all_db_modules__():
    # defined as a function so we don't actually initialize
    # all of the modules by importing them
    from . import (gameshow)

    return [gameshow]


STUB_XML = """<?xml version='1.0' standalone='yes'?>
<Databases>
	<Database name="gameshow" type="MysqlDatabase">
		<Hostname>localhost</Hostname>
		<Port></Port>
		<Username>root</Username>
		<Password></Password>
		<Db>gameshow</Db>
	</Database>
</Databases>
"""

class StubContextManager(object):

    def __enter__(self):
        pass

    def __exit__(mgr, exit, value, exc):
        unstub()


def cleanup(modules=None):
    """ Cleanup all sessions for a given module
    Use this method when you can't be sure what sessions were used in
    a given execution path.
    """
    modules = modules or __all_db_modules__()
    
    for db_module in modules:
        for db_session in ["Master", "Slave", "Analytics"]:
            session = "Scoped{}Session".format(db_session)
            getattr(db_module, session).remove()


def stub(modules=None):
    """ Stub out the database.
    """
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        modules = modules or __all_db_modules__()
        configure(modules=modules, driver="sqlite", 
                  config_file=StringIO.StringIO(STUB_XML))
        create_all(modules=modules)
    return StubContextManager()

def unstub(modules=None):
    """ Unstub all the databases
    """
    modules = modules or __all_db_modules__()
    configure(modules=modules)


def configure(modules=None, driver=None, config_file=None, scope_fn=None, pool_size=None):
    """ Setup declarative base models to replace all the engines with
    the following configuration

    :param modules: Modules is a list of three tuples
                    (module, db, base). The following is a valid tuple
                    (questions, "questions0", questions.base.QuestionBase)

    :param driver: The driver you want to use. Defaults to mysql

    :param config_file: db.xml file to read for database configuration.
                        Defaults to ~/Project/db.xml

    :param scope_fn: Function to use for scope of sessions. Defaults to thread
                     local
    """
    modules = modules or __all_db_modules__()

    params = {}

    if config_file is not None:
        params["config"] = et.parse(config_file).getroot()

    if driver is not None:
        params["driver"] = driver

    for module in modules:
        engs = configuration.engines(module.__db_name__, pool_size=pool_size, **params)
        configuration.setup_module(module.__dict__, engs=engs, scope_fn=scope_fn)

def create_all(modules=None):
    """ Create all tables for the given modules """

    for module in (modules or __all_db_modules__()):
        module.base.Declarative.metadata.create_all(module.master_engine)


def geventify(modules = None, driver=None, config_file = None, pool_size = None):
    """ Make `db.*` play well with gevent.

    This method monkey patches `db.*` to replace all of the engines
    and session factories so that they play nicely in a gevent environment.

    This method configures the DB layer to connect with pymysql (a pure python
    mysql driver) so that gevent can monkey patch the sockets it uses. It
    also sets up scoped session factories that are scoped by greenlet.

    If you want to defer queries to a thread pool with the standard MySQLdb
    driver, use `monkey.gevent_poolify`.
    """
    # monkey patch sqlalchemy's queue primitive
    # to use a queue that doesn't use non-green locking primitives
    # so that we don't block with we overflow an engine's connection pool
    # I suspect this is no longer necessary in gevent 1.0, but this needs to
    # be verified
    import sqlalchemy.util.queue as sqlaq
    import gevent.queue
    sqlaq.Queue = gevent.queue.Queue
    sqlaq.Empty = gevent.queue.Empty
    sqlaq.Full = gevent.queue.Full

    import gevent
    def scope_fn():
        return id(gevent.getcurrent())
    
    driver = driver or "mysql+pymysql"
    configure(driver = driver, scope_fn=scope_fn,
              modules=modules, config_file=config_file, pool_size=pool_size)

class BadMonkeyPatchException(Exception): pass

def _find_main_thread():
    threads = threading.enumerate()
    for thread in threads:
        if isinstance(thread, threading._MainThread):
            return thread
    raise BadMonkeyPatchException("You messed up threading, couldn't find main thread anywhere in {}".format(threads))

_main_thread = _find_main_thread()


@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    """Make sure that connections are alive"""
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:
        raise exc.DisconnectionError()
    cursor.close()


def threadpool(fn):
    from functools import wraps
    from twisted.internet.threads import deferToThread
    from twisted.internet import reactor
    import threading

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if reactor.running:
            if _main_thread == threading.current_thread():
                retval = deferToThread(fn, *args, **kwargs)
            else:
                retval = fn(*args, **kwargs)
        else:
            retval = fn(*args, **kwargs)
        return retval
    wrapper.use_threadpool = True
    return wrapper

