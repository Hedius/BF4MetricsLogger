"""
Handle BBR API

Inheritance, and a better dynamic datasource logic would be better...
"""
import json
import logging
from typing import Optional

import aiohttp

from utils import StatsEntry


class BBRAPI:
    def __init__(self):
        self.data = None

    async def update(self):
        """
        Update the data from the official BBR API
        """
        headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip,deflate'
        }
        url = 'https://publicapi.battlebit.cloud/Servers/GetServerList'
        try:
            async with aiohttp.get(url, headers=headers) as r:
                # Dirty... :)
                data = (await r.text()).encode().decode('utf-8-sig')
                self.data = json.loads(data)
        except (TypeError, aiohttp.ClientError, aiohttp.ContentTypeError,
                json.JSONDecodeError) as e:
            logging.error(f'Fetch from BBR API failed: {e}')

    async def get_server_status(self, name: str) -> Optional[StatsEntry]:
        """
        Get the player count and current map of the given server
        Also saves the result in class members
        :param name: name of the server. matching is done by name.
        :returns: the player status dataclass
        """
        if not self.data:
            return
        for server in self.data:
            if server['Name'] != name:
                continue
            return StatsEntry(
                mode=server['Gamemode'],
                map=server['Map'],
                players=server['Players'],
                queue=server['QueuePlayers'],
            )
