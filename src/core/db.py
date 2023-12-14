from mysql import connector
from typica import BaseConnection, ConnectionMeta, ConnectionUriMeta

from src.common import envs


# ? Single Usage
class MainSQL(BaseConnection):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            ConnectionMeta(
                host=envs.SQL_HOST,
                port=envs.SQL_PORT,
                username=envs.SQL_USERNAME,
                password=envs.SQL_PASSWORD,
                database=envs.SQL_DATABASE,
            )
        )
        self.client = connector.connect(
            host=self._metadata.host,
            port=self._metadata.port,
            user=self._metadata.username,
            password=self._metadata.password,
            database=self._metadata.database,
            **kwargs,
        )
        self.cursor = self.client.cursor()
