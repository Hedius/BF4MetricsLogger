import logging

from .MariaDB.Connector import Connector as MariaDB


class AdKatsDB(MariaDB):
    """Connector to the AdKatsDB"""

    def __init__(self, host, port, database, user, pw):
        super().__init__(host, port, database, user, pw)

    async def get_status_of_servers(self):
        """Return the status of all servers"""
        command = """\
        SELECT ts.serverID AS server_id, ts.ServerGroup AS server_group,
            ts.ServerName as name,
            ts.usedSlots AS used_slots,
            ts.maxSlots AS max_slots,
            tg.Name AS game,
            bss.battlelog_guid AS guid
        FROM tbl_server ts
        INNER JOIN tbl_games tg ON ts.gameID = tg.gameID
        LEFT OUTER JOIN bfacp_settings_servers bss
            ON ts.ServerID = bss.server_id
        WHERE ConnectionState != 'off'
        """
        try:
            results = await self.exec(command)
        except self.DBException as e:
            logging.exception('AdKatsDB> Error while fetching server status'
                              f' from AdKats!\n{e}')
            raise e

        if len(results) == 0:
            logging.info('AdKatsDB> Found 0 servers!')
            return None
        logging.debug(
            f'AdKatsDB> received server status for {len(results)} servers')
        return results
