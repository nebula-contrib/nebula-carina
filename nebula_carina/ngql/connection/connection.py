import threading

from nebula3.Exception import IOErrorException
from nebula3.data import ResultSet
from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config

from nebula_carina.ngql.errors import NGqlError, DefaultSpaceNotExistError
from nebula_carina.settings import database_settings


# TODO: fix connection / connection pool / session in a robust way later

config = Config()
config.max_connection_pool_size = database_settings.max_connection_pool_size
connection_pool = ConnectionPool()


def _split(server_address: str) -> tuple[str, int]:
    ip, port = server_address.split(':', 1)
    return ip, int(port)


if not connection_pool.init([_split(i) for i in database_settings.servers], config):
    raise RuntimeError('Cannot connect to the connection pool')


class LocalSession(object):
    _lock = threading.Lock()
    _instance = None
    _main_session = None
    _space_settled = False

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance.create_session()
                cls._instance._space_settled = False
        return cls._instance

    @property
    def session(self):
        return self._main_session

    def create_session(self):
        self._main_session = connection_pool.get_session(
            user_name=database_settings.user_name, password=database_settings.password
        )

    def recover_session(self):
        with self._lock:
            self.create_session()
            self.settle_space()

    def raw_use_space(self, name):
        self._main_session.execute(f'USE {name};')

    def raw_show_spaces(self) -> list[str]:
        return [i.as_string() for i in self._main_session.execute('SHOW SPACES;').column_values('Name')]

    def settle_space(self):
        try:
            if database_settings.default_space not in self.raw_show_spaces():
                raise DefaultSpaceNotExistError(database_settings.default_space)
            self.raw_use_space(database_settings.default_space)
            self._space_settled = True
        except (IOErrorException, RuntimeError):
            if not self._main_session.ping():
                LocalSession().recover_session()
            else:
                raise

    @property
    def space_settled(self):
        return self._space_settled

    def run_ngql(self, ngql: str, *, is_spacial_operation=False) -> ResultSet:
        if not is_spacial_operation and not self.space_settled:
            self.settle_space()
        try:
            result = self._main_session.execute(ngql)
        except (IOErrorException, RuntimeError):
            if not self._main_session.ping():
                self.recover_session()
                result = self.session.execute(ngql)
            else:
                raise
        if result.error_code() < 0:
            if 'Session not existed!' in result.error_msg():
                self.recover_session()
                result = self.session.execute(ngql)
                if result.error_code() < 0:
                    raise NGqlError(result.error_msg(), result.error_code(), ngql)
            else:
                raise NGqlError(result.error_msg(), result.error_code(), ngql)
        return result


def run_ngql(
        ngql: str, *,
        is_spacial_operation=False
) -> ResultSet:
    return LocalSession().run_ngql(ngql, is_spacial_operation=is_spacial_operation)


from nebula_carina.ngql.schema.space import create_space, show_spaces  # noqa
if database_settings.auto_create_default_space_with_vid_desc and database_settings.default_space not in show_spaces():
    create_space(
        database_settings.default_space,
        database_settings.auto_create_default_space_with_vid_desc,
        if_not_exists=True
    )
