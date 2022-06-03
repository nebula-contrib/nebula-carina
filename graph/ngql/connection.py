from nebula3.data import ResultSet
from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config

from graph.ngql.errors import NGqlError
from graph.settings import database_settings

config = Config()
config.max_connection_pool_size = database_settings.max_connection_pool_size
connection_pool = ConnectionPool()


def _split(server_address: str) -> tuple[str, int]:
    ip, port = server_address.split(':', 1)
    return ip, int(port)


if not connection_pool.init([_split(i) for i in database_settings.servers], config):
    raise RuntimeError('Cannot connect to the connection pool')


def run_ngql(ngql: str) -> ResultSet:
    session = connection_pool.get_session(user_name=database_settings.user_name, password=database_settings.password)
    result = session.execute(ngql)
    session.release()
    if result.error_code() < 0:
        raise NGqlError(result.error_msg(), result.error_code())
    return result
