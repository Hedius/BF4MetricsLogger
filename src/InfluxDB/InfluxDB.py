import datetime

import influxdb_client


class InfluxDB:
    def __init__(self, host, bucket, org, token):
        """
        InfluxDB client
        :param host:
        :param bucket:
        :param org:
        :param token:
        """
        self.host = host
        self.bucket = bucket
        self.org = org
        self.token = token

        self._client = None

    @property
    def client(self) -> influxdb_client.InfluxDBClient:
        """
        Get a influxDB connection socket
        :return:
        """
        client = influxdb_client.InfluxDBClient(
            url=self.host,
            token=self.token,
            org=self.org
        )
        return client

    def log(self, server_id, used_slots, seeded_slots, max_slots):
        """
        Log the given data to influx
        :param server_id:
        :param used_slots:
        :param seeded_slots:
        :param max_slots:
        :return:
        """
        measurement = {
            'measurement': 'server_status',
            'tags': {'server_id': server_id},
            'fields': {
                'used_slots': used_slots,
                'seeded_slots': seeded_slots,
                'max_slots': max_slots
            },
            'time': datetime.datetime.utcnow()
        }

        # log data
        with self.client as client:
            with client.write_api() as write_client:
                write_client.write(
                    self.bucket,
                    self.org,
                    measurement
                )
