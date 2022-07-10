from nebula3.data import ResultSet
from nebula3.gclient.net import ConnectionPool, Session
from nebula3.Config import Config

from nebula_model.ngql.errors import NGqlError, DefaultSpaceNotExistError
from nebula_model.settings import database_settings

config = Config()
config.max_connection_pool_size = database_settings.max_connection_pool_size
connection_pool = ConnectionPool()


def _split(server_address: str) -> tuple[str, int]:
    ip, port = server_address.split(':', 1)
    return ip, int(port)


if not connection_pool.init([_split(i) for i in database_settings.servers], config):
    raise RuntimeError('Cannot connect to the connection pool')
main_session = connection_pool.get_session(user_name=database_settings.user_name, password=database_settings.password)
space_settled = False


def run_ngql(
        ngql: str, session: Session = None, *,
        is_spacial_operation=False
) -> ResultSet:
    global space_settled
    if not session:
        session = main_session
    if not is_spacial_operation and not space_settled:
        space_settled = True
        from nebula_model.ngql.schema.space import use_space, show_spaces
        if database_settings.default_space not in show_spaces():
            raise DefaultSpaceNotExistError(database_settings.default_space)
        use_space(database_settings.default_space)
    result = session.execute(ngql)
    if result.error_code() < 0:
        raise NGqlError(result.error_msg(), result.error_code(), ngql)
    return result
