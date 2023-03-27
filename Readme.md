# BF4 Metrics Logger

[![pipeline status](https://gitlab.com/e4gl/bf4metricslogger/badges/main/pipeline.svg)](https://gitlab.com/e4gl/bf4metricslogger/-/commits/main)
[![Discord](https://img.shields.io/discord/388757799875903489.svg?colorB=7289DA&label=Discord&logo=Discord&logoColor=7289DA&style=flat-square)](https://discord.e4gl.com/)
<!-- [![Docker Pulls](https://img.shields.io/docker/pulls/hedius/bf4metricsloggger.svg?style=flat-square)](https://hub.docker.com/r/hedius/bf4metricslogger/) -->

This python app uses your PRoCon DB (Stats Logger) and GameStatsAPI to log the following metrics to an InfluxDB:
* Used Slots
* Seeded Slots
* Max Slots
* Queue
* Map
* Game mode
* Favorites (In-Game)

**Influx stats**:
 * Tags: server_id, GUID
 * Measurement: server_status
 * Fields: used_slots, seeded_slots, max_slots, queue, map, mode, favorites

# Setup
## 1. docker (docker-compose)
 1. clone the repository
 2. cp config.ini.example config.ini
 3. adjust config.ini
 4. sudo docker-compose up -d
 
# Updating
## docker-compose
1. sudo docker-compose down --rmi all
2. git pull
3. sudo docker-compose up -d

# Configuration
## 1. Config file -> Mount to /usr/src/app/config.ini
```ini
[General]
logging_interval = 60

[AdKatsDB]
host =
port =
db =
user =
pw =

[InfluxDB]
host =
org =
bucket =
token =
```
    
# License
This project is free software and licensed under the GPLv3.
