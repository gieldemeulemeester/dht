[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://raw.githubusercontent.com/manbearwiz/youtube-dl-server/master/LICENSE)

# dht

*dht* is a Docker image for [*adafruit-circuitpython-dht*](https://github.com/adafruit/Adafruit_CircuitPython_DHT), a Python driver for DHT11 and DHT22 temperature-humidity sensors.
The docker image is based on [*python:3.8*](https://registry.hub.docker.com/_/python/). The sensor is queried, temperature and humidity are logged to a time-series database using [*influxdb-python*](https://github.com/influxdata/influxdb-python).

## Running

### Docker

This example uses the `docker build` command to build the image and the `docker run` command to create a container from that image.

```shell
docker build --tag dht .
docker run -d dht
```

### Docker Compose

This is an example service definition that could be added in `docker-compose.yml`. The *dht* service depends on the *influxdb* service for data logging.

```yml
dht:
    container_name: dht
    build: ./services/dht/
    depends_on:
      - influxdb
    environment:
      - HOST_HOSTNAME=daeron
      - INFLUXDB_HOST=influxdb
      - INFLUXDB_PORT=8086
      - INFLUXDB_DB=iot
      - INFLUXDB_USER=<insert user>
      - INFLUXDB_PASSWORD=<insert password>
      - INFLUXDB_RETENTION_POLICY=raw
      - INFLUXDB_MEASUREMENT=air
      - DHT_INTERVAL=5
    devices:
      - /dev/gpiomem:/dev/gpiomem
    privileged: true
    restart: unless-stopped

influxdb:
    container_name: influxdb
    image: influxdb:latest
    environment:
      - INFLUXDB_DB=<insert db>
      - INFLUXDB_DATA_ENGINE=tsm1
      - INFLUXDB_REPORTING_DISABLED=false
      - INFLUXDB_HTTP_AUTH_ENABLED=true
      - INFLUXDB_ADMIN_ENABLED=true
      - INFLUXDB_ADMIN_USER=admin
      - INFLUXDB_ADMIN_PASSWORD=<insert password>
    volumes:
      - ./volumes/influxdb/data:/var/lib/influxdb
      - ./volumes/influxdb/backup:/var/lib/influxdb/backup
    ports:
      - 8086:8086
      - 8083:8083
      - 2003:2003
    restart: always
```
