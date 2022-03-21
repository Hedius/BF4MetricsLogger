import asyncio
import datetime
import logging
import time
from argparse import ArgumentParser
from configparser import ConfigParser
from pathlib import Path
from typing import Tuple

from AdKatsDB.AdKatsDB import AdKatsDB
from GameStatsAPI.GameStatsAPI import GameStatsAPI
from InfluxDB.InfluxDB import InfluxDB


class PlayerCountLogger:
    def __init__(self, adk: AdKatsDB, api: GameStatsAPI, influx: InfluxDB,
                 log_interval=60):
        """
        Init PlayerCountLogger
        :param adk:
        :param api:
        :param influx:
        :param log_interval: repeat logging every x seconds
        """
        self.adk = adk
        self.api = api
        self.influx = influx
        self.log_interval = log_interval

    async def _get_seeded_count(self, name: str, battlelog_id):
        """
        Get the seeded player count for the given server
        :param name:
        :param battlelog_id:
        :return:
        """
        servers = await self.api.get_bf4_servers(name)

        for server in servers['servers']:
            if battlelog_id == server['battlelogId']:
                return server['playerAmount']

        logging.critical(f'Unable to find API profile for {name}')
        return 0

    async def check(self):
        servers = await self.adk.get_status_of_servers()

        for server in servers:
            seeded_count = await self._get_seeded_count(server.name,
                                                        server.guid)

            # this one is synchronous :) makes the whole async stuff useless
            # lazy
            self.influx.log(
                server_id=server.server_id,
                used_slots=server.used_slots,
                seeded_slots=seeded_count,
                max_slots=server.max_slots
            )

    def run(self):
        loop = asyncio.get_event_loop()
        try:
            while True:
                # useless async
                # dirty workaround to have a nearly perfect logging interval
                # (:
                start = datetime.datetime.now()

                loop.run_until_complete(self.check())

                done = datetime.datetime.now()
                delta = (done - start).total_seconds()
                time.sleep(self.log_interval - delta)
        finally:
            loop.close()


def read_config(file_path: Path) -> Tuple[int, AdKatsDB, InfluxDB]:
    """
    Read the config
    :param file_path:
    :return: logging_interval, adk, influx
    """
    parser = ConfigParser()
    parser.read(file_path)

    section = parser['General']
    logging_interval = section.getint('logging_interval', 60)

    section = parser['AdKatsDB']
    adk = AdKatsDB(
        host=section['host'],
        port=int(section['port']),
        user=section['user'],
        pw=section['pw'],
        database=section['db'],
    )

    section = parser['InfluxDB']
    influx = InfluxDB(
        host=section['host'],
        org=section['org'],
        bucket=section['bucket'],
        token=section['token'],
    )
    return logging_interval, adk, influx


def main():
    parser = ArgumentParser(description='E4GL InfluxDB PlayerCount Logger')
    parser.add_argument(
        '-c', '--config',
        help='Path to config file',
        required=True,
        dest='config'
    )
    args = parser.parse_args()

    logging_interval, adk, influx = read_config(args.config)
    api = GameStatsAPI()

    logger = PlayerCountLogger(adk, api, influx, logging_interval)
    logger.run()


if __name__ == '__main__':
    main()
