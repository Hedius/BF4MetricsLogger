import asyncio
import datetime
import logging
import time
from argparse import ArgumentParser
from configparser import ConfigParser
from pathlib import Path
from typing import Tuple

from AdKatsDB.AdKatsDB import AdKatsDB
from BBRAPI.BBRAPI import BBRAPI
from GameStatsAPI.GameStatsAPI import GameStatsAPI, GameStatsAPIException
from InfluxDB.InfluxDB import InfluxDB
from utils import StatsEntry


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
        self.bbr = BBRAPI()
        self.influx = influx
        self.log_interval = log_interval

    async def _get_server_stats(self, name: str, battlelog_id):
        """
        Get the server status for the given server.
        :param name:
        :param battlelog_id:
        :return:
        """
        try:
            server = await self.api.get_bf4_server_detailed(name)
        except GameStatsAPIException as e:
            logging.error(str(e))
            return
        except asyncio.exceptions.TimeoutError:
            logging.error('GameStatsAPI request ended in a timeout.')
            return

        if battlelog_id in server['serverLink']:
            return StatsEntry(
                mode=server['mode'],
                map=server['currentMap'],
                players=server['playerAmount'],
                queue=server['inQueue'],
                favorites=int(server['favorites']),
            )

        logging.critical(f'Unable to find API profile for {name}')
        return None

    async def check(self):
        await self.bbr.update()
        servers = await self.adk.get_status_of_servers()

        for server in servers:
            server_stats = None
            if server.game == 'BF4':
                if server.guid is not None:
                    server_stats = await self._get_server_stats(server.name,
                                                                server.guid)
            elif server.game == 'BBR':
                server_stats = await self.bbr.get_server_status(server.name)
            if server_stats is None:
                server_stats = StatsEntry()

            # this one is synchronous :) makes the whole async stuff useless
            # lazy
            self.influx.log(
                server_id=server.server_id,
                used_slots=server.used_slots,
                seeded_slots=server_stats.players,
                max_slots=server.max_slots,
                queue=server_stats.queue,
                mode=server_stats.mode,
                cur_map=server_stats.map,
                favorites=server_stats.favorites,
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
