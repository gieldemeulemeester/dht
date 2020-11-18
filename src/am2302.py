#!/usr/bin/env python
#coding=utf8

import adafruit_dht, board, argparse, sys, os, json, socket, schedule, time
from datetime import datetime
from influxdb import InfluxDBClient

def log_influx(temperature, humidity):
    client = InfluxDBClient(os.environ['INFLUXDB_HOST'], os.environ['INFLUXDB_PORT'], os.environ['INFLUXDB_USER'], os.environ['INFLUXDB_PASSWORD'], os.environ['INFLUXDB_DB'])
    point = [
        {
            "retention_policy": os.environ['INFLUXDB_RETENTION_POLICY'],
            "measurement": os.environ['INFLUXDB_MEASUREMENT'],
            "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            "tags": {
                "host": os.environ['HOST_HOSTNAME']
            },
            "fields": {
                "temperature": float(temperature),
		"humidity": float(humidity)
            }
        }
    ]
    client.write_points(point)

def get_measurements(args):
    dht = adafruit_dht.DHT22(board.D4)
    temperatures = []
    humidities = []

    for c in range(args.count):
        temperature = dht.temperature
        humidity = dht.humidity

        if temperature is not None and humidity is not None:
            temperatures.append(temperature)
            humidities.append(humidity)
            if args.isVerbose and args.count > 1:
                if args.isJsonEncoded:
                    print("{0}: {1}".format(c + 1, json.dumps({'temperature': round(temperature, 1), 'humidity': round(humidity/100, 3)})))
                else:
                    print("{0}: {1:0.1f}°C, {2:0.1f}%".format(c + 1, temperature, humidity))
        else:
            if args.isVerbose or args.count == 1:
                print("failed")
        if c < args.count - 1:
            time.sleep(2)

    if len(temperatures) > 0 and len(humidities) > 0:
        medianTemperature = get_median(temperatures)
        medianHumidity = get_median(humidities)

        if args.isVerbose and args.count > 1:
            print("-----------------")

        if args.isJsonEncoded:
            print(json.dumps({'temperature': round(medianTemperature, 1), 'humidity': round(medianHumidity, 1)}))
        else:
            print("{0:0.1f}°C, {1:0.1f}%".format(medianTemperature, medianHumidity))

        if args.isLogging:
            log_influx(medianTemperature, medianHumidity)

def get_median(values):
    values.sort()

    if len(values) % 2 == 0: return (values[len(values)//2] + values[len(values)//2 - 1])/2
    else: return values[len(values)//2]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Measure temperature and humidity with sensor AM2302.")
    parser.add_argument('-n', '--count', type=int, default=1, help="number of measurements")
    parser.add_argument('-j', '--json', action='store_true', dest='isJsonEncoded', help="JSON encoded output")
    parser.add_argument('-L', '--log', action='store_true', dest='isLogging', help="log output to influx database")
    parser.add_argument('-v', '--verbose', action='store_true', dest='isVerbose', help="print debug information")
    parser.add_argument('-i', '--interval', type=int, default=os.environ['DHT_INTERVAL'], help="minutes of delay between repeats, no repeats when zero")
    args = parser.parse_args()

    get_measurements(args)

    if args.interval < 0:
        sys.exit(2)
    elif args.interval > 0:
        schedule.every(args.interval).minutes.do(get_measurements, args)
        while True:
            schedule.run_pending()
            time.sleep(1)
