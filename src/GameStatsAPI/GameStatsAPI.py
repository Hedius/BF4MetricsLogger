import asyncio.exceptions

import aiohttp
from urllib.parse import quote


class GameStatsAPIException(Exception):
    """
    Wrapper for API exceptions.
    """
    pass


class GameStatsAPI:
    """
    API wrapper for the GameStatsAPI.
    """
    def __init__(self, base_url='https://api.gametools.network'):
        """
        API wrapper for the GameStatsAPI.
        """
        self._base_url = base_url

        self._headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip,deflate',
            'User-Agent': 'Mozilla/5.0 (compatible; E4GL; PlayerCountLogger)'
        }

    async def api_request(self, url: str, **kwargs):
        """
        Perform an API request
        :param url: url to retrieve. (without the API base!)
        :param kwargs: args for aiohttp.ClientSession.get()
        :return: parsed data Lists / Dicts
        :raises GameStatsAPIException: if the return code is > 300
        """
        full_url = self._base_url.rstrip('/') + '/' + url.lstrip('/')
        # We really should reuse sessions, but tbh: IDC :)
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(headers=self._headers) as s:
            async with s.get(full_url, timeout=timeout,
                             **kwargs) as r:
                if r.status > 300:
                    raise GameStatsAPIException(
                        f'API Request failed: {await r.text()}')
                json = await r.json()
                return json

    async def get_bf4_servers(self, name):
        """
        Get bf4 servers by name.
        :param name: server name
        :return: results
        """
        return await self.api_request(
            f'/bf4/servers/?name={quote(name)}&region=all&platform=pc&limit=50&lang=en-us'
        )

    async def get_bf4_server_detailed(self, name):
        """
        Get bf4 servers by name.
        :param name: server name
        :return: results
        """
        return await self.api_request(
            f'/bf4/detailedserver/?name={quote(name)}&region=all&platform=pc&lang=en-us'
        )
