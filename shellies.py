import concurrent.futures
import configparser
import logging
import requests
import signal
from datetime import datetime
from influxdb_client import InfluxDBClient
from time import sleep

# Set this to logging.DEBUG in odrder to see debugging messages
loglevel = logging.INFO
MAX_ERRORS = 5


def sigint_handler(signum, frame):
    global interrupted

    interrupted = True
    logging.info("Interrupted, waiting for threads to finish...")


def record_shelly_measurements(shelly):
    global interrupted
    tolerate_errors = MAX_ERRORS
    
    logging.debug(f"Thread for {shelly} started")

    with InfluxDBClient.from_config_file("influxdb.ini") as dbclient:
        while True:
            sleep(30)

            try:
                r = requests.post(f"http://{shelly}/rpc",
                    data='{"id":1,"method":"Switch.GetStatus","params":{"id":0}}')
                tolerate_errors = MAX_ERRORS
            except Exception as err:
                logging.error(f"{shelly} can't read switch status ({err})")
                tolerate_errors = tolerate_errors - 1
                if tolerate_errors == 0:
                    logging.critical(f"{shelly} too many errors. Giving up.")
                    return
                else:
                    continue

            try:
                status = r.json()
            except Exception as err:
                logging.critical(f"{shelly} returned invalid data")

            measurement = {
                "measurement": "electricity_consumption",
                "tags": {
                    "source": status['src']
                },
                "time": datetime.utcnow(),
                "fields": {
                    "state": bool(status['result']['output']),
                    "power": float(status['result']['apower']),
                    "voltage": float(status['result']['voltage']),
                    "current": float(status['result']['current']),
                    "temperature": float(status['result']['temperature']['tC'])
                }
            }
            
            logging.debug(f"{shelly} returned {measurement}")

            with dbclient.write_api() as dbwriter:
                try:
                    dbwriter.write(bucket="shelly", record=measurement)
                except Exception as err:
                    logging.critical(f"{shelly} can't write to database ({err})")

            if interrupted:
                break


if __name__ == "__main__":
    interrupted = False

    logging.basicConfig(level=loglevel)

    signal.signal(signal.SIGINT, sigint_handler)

    config = configparser.ConfigParser()
    config.read("shellies.ini")
    shellies = config['shellies']['shellies'].split()

    logging.debug(f"Found these shellies: {shellies}")

    logging.info("shellies starting up, spinning up threads...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(shellies)) as executor:
        executor.map(record_shelly_measurements, shellies)
