import StringIO
import sqlalchemy
import collections
import sqlalchemy, collections, xml.etree.ElementTree as et
from sqlalchemy.orm import sessionmaker, scoped_session, Session

DEFAULT_DB_CONFIG_FILE = "/Users/adam/Projects/potent-potables/db.xml"

DB_MSG = """Could not find database {0}. Please add:
    <Database name="{0}" type="MysqlDatabase">
        <Hostname>localhost</Hostname>
        <Port></Port>
        <Username>root</Username>
        <Password></Password>
        <Db>{0}</Db>
    </Database>
to your db.xml configuration file.
"""

class DbNotFound(Exception):
    pass

class ConfigurationError(Exception):
    pass

def engines(db_name,
           driver = "mysql+mysqldb",
           config = None,
           pool_size = None,
           **kwargs):
    """Get `sqlalchemy.Engine` objects for a database.

    Reads the `config_file` to parse out the connection information for
    the database specified by `db_name`. If not slave or analytics
    connection information is configured, they will 'fall back' to
    be the same the master and slave connections, respectively.

    :returns: A 3-tuple of `sqlalchemy.Engine` objects representing
        connection information for connecting to the master,
        slaves and analytics roles for the the requested database.

    :param db_name: Name of a database
        e.g. gameshows, etc.

    :param config_file: File name or file object of the xml
        file containing connection information for databases.

    :param kwargs: Keyword arguments to be passed through to
        `sqlalchemy.create_engine` when creating the database engines.

    :exception DbNotFound: Thrown if the configuration file contains
        no information for connecting to the master.

    :exception ConfigurationError: Thrown if the requested database
        configuration is missing a required property.
    """
    def _engine(db_name,
                role,
                driver,
                root,
                charset = 'utf8',
                **kwargs):
        """ helper function for creating a single engine """

        db_name = "{}-{}".format(db_name, role) if role else db_name
        e = root.find(".//Database[@name='{}']".format(db_name))
        if e is None:
            raise DbNotFound(DB_MSG.format(db_name))

        Props = collections.namedtuple('DBProperties', ['hostname', 'port', 'db',
                                                        'username', 'password'])
        def t(propname):
            try:
                return e.find(propname).text
            except AttributeError:
                raise ConfigurationError(
                    "Could not find property '{}' for Database '{}'".format(
                        propname, db_name))

        props = Props(
            hostname = t("Hostname"),
            port = t("Port"),
            username = t("Username"),
            password = t("Password"),
            db = t("Db")
        )

        if driver == "sqlite":
            uri = "sqlite://"
            default_opts = {}
        else:
            uri = ("{driver}://{username}:{password}@"
                  "{hostname}:{port}/{db}?charset={charset}").format(
                driver = driver,
                username = props.username or "root",
                password = props.password or "",
                port = props.port or 3306,
                hostname = props.hostname,
                db = props.db,
                charset = charset)

            default_opts = dict(
                pool_size = pool_size or 10,
                pool_timeout = 10,
                pool_recycle = 60,
                )

        default_opts.update(kwargs)
        return sqlalchemy.create_engine(uri, **default_opts)

    # read the config file only once
    if config is None:
        config = et.parse(DEFAULT_DB_CONFIG_FILE).getroot()

    root = config

    # return type
    EngineTuple = collections.namedtuple("EngineTuple",
                                         ["master", "slave", "analytics"])

    def curried_engine(db_name, role = ""):
        return _engine(db_name, role, driver, root, **kwargs)

    # get the master
    try:
        master_engine = curried_engine(db_name, "master")
    except DbNotFound:
        master_engine = curried_engine(db_name)

    # get the slave
    try:
        slave_engine = curried_engine(db_name, "slave")
    except DbNotFound:
        # no slave config? then slave maps to master
        slave_engine = master_engine

    # get the analytics
    try:
        analytics_engine = curried_engine(db_name, "analytics")
    except DbNotFound:
        # no analytics? then analytics maps to slaves
        analytics_engine = slave_engine

    return EngineTuple(master_engine, slave_engine, analytics_engine)


def setup_module(module, engs = None, scope_fn = None):
    """ Setup the engines, scoped sessions and query properties
    for a module and its base class.

    :param module: The module's dictionary in which to inject the
        generated engine and session objects.

    :param db_name: The database to use to configure the generated
        objects.

    :param base_class: The base class of the database on which to
        install the query properties.
    """

    db_name = module['__db_name__']
    base_class = module['__base_class__']

    class ReadOnlySession(Session):
        def flush(self, *args, **kwargs):
            if any(map(bool, [self.dirty, self.new, self.deleted])):
                raise AssertionError("All non-master databases are read-only.")

    def setup_module(db_type):
        engine_name = '{}_engine'.format(db_type)
        sess_name = '{}Session'.format(db_type.capitalize())
        scoped_sess_name = 'Scoped{}'.format(sess_name)
        query_prop_name = 'query_{}'.format(db_type)
        short_query_prop_name = 'q{}'.format(db_type[0])
        sess_class = Session if db_type == 'master' else ReadOnlySession

        Factory = sessionmaker(bind = module[engine_name], class_ = sess_class)
        ScopedFactory = scoped_session(Factory, scopefunc = scope_fn)
        module[sess_name] = Factory
        module[scoped_sess_name] = ScopedFactory

        for prop in module.values():
            # fun with python introspection
            # what we want to do is set up a query property on every class in the module
            # that is a subclass of the module's base class
            try:
                isdbclass = issubclass(prop, base_class)
            except TypeError as e:
                isdbclass = False
            
            if isdbclass:
                print "format:{}".format(prop.__query_cls__)
                qprop = ScopedFactory.query_property(query_cls = prop.__query_cls__)
                setattr(prop, query_prop_name, qprop)
                setattr(prop, short_query_prop_name, qprop)

    (module['master_engine'],
     module['slave_engine'],
     module['analytics_engine']) = engs or engines(db_name)

    setup_module('master')
    setup_module('slave')
    setup_module('analytics')

