from typing import Optional

import aiomysql
import re


class AttrDict(dict):
    """Dict that can get attribute by dot, and doesn't raise KeyError"""

    def __getattr__(self, name):
        return self[name]
        # try:
        #     return self[name]
        # except KeyError:
        #     return None


class AttrDictCursor(aiomysql.DictCursor):
    dict_type = AttrDict


class Connector:
    """SQL connector for MySQL/MariaDB sql servers"""

    def __init__(self, host, port, database, user, pw):
        self._host = host
        self._port = port
        self._database = database
        self._user = user
        self._password = pw

        self._pool: Optional[aiomysql.Pool] = None

    def __del__(self):
        """destructor - close connection"""
        self._close()

    async def _connect(self):
        """Connect to a MariaDB server and set/return the connection socket if
        needed.
        """
        # return active connection
        if self._pool:
            return self._pool

        # reconnect
        try:
            self._pool = await aiomysql.create_pool(
                maxsize=25,
                host=self._host,
                port=self._port,
                db=self._database,
                user=self._user,
                password=self._password,
                autocommit=False)
        except Exception as e:
            raise self.DBException(str(e))
        return self._pool

    def _close(self):
        """close the connection to the MariaDB server"""
        # return active connection
        if self._pool:
            self._pool.close()
            self._pool = None

    async def exec(self, query, args=None, commit=True):
        """Execute the given command with args
        :param query: sql query
        :param args: arguments
        :param commit: commit after the request
        :returns: result as a list
        """
        # support for multi queries?
        pool = await self._connect()
        try:
            async with pool.acquire() as conn:
                async with conn.cursor(AttrDictCursor) as cursor:
                    await cursor.execute(query, args)
                    results = await cursor.fetchall()
                    if commit:
                        await conn.commit()
        except Exception as e:
            raise self.SQLException(f'Execution of query failed!: {e}')
        return results

    def validate_term(self, term):
        if re.match(r'^[a-zA-Z0-9!._-öäü]+$', term) is None:
            raise self.DBException('Invalid Parameter: ' + term)

    # exception
    class DBException(Exception):
        pass

    class SQLException(DBException):
        pass
