# shellies
A simple program for reading statistics from a Shelly device and writing them to an Influx database.

## Background
I wondered if I could charge my electric toothbrush during the cheap night hours, without having to plug and pull the charger's cord every day. As it appears, a [Shelly power metering switch](https://www.shelly.cloud/en/products/shop/shelly-plus-1-pm-2-pack/shelly-plus-1-pm) was exactly what I needed and so I bought one. And since it has an [API](https://shelly-api-docs.shelly.cloud/gen2/) I thought it would be nice to collect some data from it and store it in an InfluxDB database, which I already had in place.

## Usage
Simply grab the the files in this repository, edit the config files, and launch the program with, e.g. `nohup python shellies.py &`.

The config files are simple: the `influxdb.ini` contains necessary things for the program to connect to your database, and the `shellies.ini` contains the names your Shelly devices are findable in your network (space separated list).
