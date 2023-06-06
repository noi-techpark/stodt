<!--
SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

SPDX-License-Identifier: CC0-1.0
-->

# STODT

[![CI/CD](https://github.com/noi-techpark/stodt/actions/workflows/main.yml/badge.svg)](https://github.com/noi-techpark/stodt/actions/workflows/main.yml)

## Purpose

The aim of this project is to provide a tool capable to analyze historical traffic and environmental data to predict pollution levels in the city of Bolzano-Bozen. The purpose of this tool is to provide a simplified overview that shows the best moment(s) to go out and do physical activity to its users.

## Data Analysis

The data used to train the model is taken from [Bolzano's Open Data Hub](https://opendatahub.bz.it/).

The datasets (or **categories**) analyzed are the following:

- Bluetooth Stations
- Parking Stations
- Weather Stations
- Environment Stations
- Traffic Stations

Each station manages many `data_types` and for each of these it is possible to obtain` records` for a given period.

Training-Data was collected within the period March-December 2019 because previous data was too inconsistent for the purpose of this project. Since the Open Data Hub collects data of stations throughout the entire region, we have filtered the sensors to the city of Bolzano only. [Here]((https://www.google.com/maps/d/u/0/edit?hl=it&mid=1PlgMh3NPWwVAzn9JwX5sObwoswnM4Qvl&ll=46.48575771659827%2C11.3225693267118&z=14)) you can have a look at the map of the stations that were taken into account (the `Traffic Stations` are about 200 so we overlayed the pointers present in map).

Only a few stations on the map were taken into consideration mainly because not all of them provide reliable data.

### Data strutures

Each station of a given`data_type`, provides records that contain:

- Period: how many seconds separate observations from each other;
- Timestamp: observation date in unix time;
- Value: the value of the record.

We decided to uniform data entries to have periods of 300 seconds. Entries with periods greater than 300 seconds will be splitted in two or more entries by assigning values as follows:
  * if it represents a **counter**, it is divided by the number of entries created.
  * if it represents an **average**, it is preserved in all created entries.

Timestamps will be adjusted according to generated entries.

### Stations

#### Traffic Stations

Did not contain any useful data in the analyzed period.

#### Bluetooth Stations

Count the number of vehicles in transit by tracking the bluetooth devices mounted on the vehicles.

These sensors are distributed in strategic locations of the city. In particular, we collect the number of light and heavy vehicles in transit.

All of these stations provide counters.

#### Weather Stations

Collect humidity, temperature, wind-speed, pressure and precipitation.

We have only one station that collects this type of data in the analyzed area but we are confident that there should be no significant variations between different areas of the city.

All these stations provide averages except for precipitation, which represents a counter.

#### Parking Stations

Provide the number of parked vehicles.

They are concentrated in the area of the station / historic city center.

These stations provide averages.

#### Environment Stations

Are stations that are distributed evenly across the city. We collect pollution levels for various indicators, specifically:

- PM2.5 - Ultra-thin powders
- PM10 - Fine powders
- CO - Carbon monoxide
- NOX - Nitrogen oxides

These stations provide averages.

### What indicator we decided to predict

We've decided to build a model capable of predicting the `PM2.5 - Ultra-thin powders` pollution levels,  because they are more dangerous for human health than` PM10 - Fine powders` and `CO - Carbon monoxide`.

We've come to observe that this indicator has two main periodic occurrences:

- daily: it tends to rise gradually during the day and to go down at night;
- weekly: it seems that PM2.5 accumulate daily and go down after about a week (usually during the weekend).

One of the factors that seems to alter these cyclicity is the presence of rainfall.

## Components

The project is written entirely in python and we have set up a `docker` image to execute specific commands. 

It is therefore necessary to build the image using:

```
./run build
```

We have chosen to create a **recurrent neural network** which takes a time series as input to predict a future snapshot of that time series itself.

Like any other machine learning algorithm, the following also makes use of an `ETL` chain:

- Extraction: via download from the OpenDataHub
- Transformation: data aggregation to "normalize" time series
- Loading: loading the normalized data to train the model

### Neural network

The `neural.py` file actually contains the model of the neural network. Some of the parameters are configurable using the `config.json` file. The time series taken into account correspond to an entire day. Therefore, if you want to predict any day, it is necessary to have the data of the whole previous day.

### ETL

#### Estraction

The file is `download.py`, it can be run in two ways:

- `./run download`: uses the configurations in `config.json` to download a specific period of data.
- `./run download batch`: downloads the last 10 days (past midnight). It is used by the live application. Retention is purposely set to 10 days to avoid unnecessarily large data sets. 

The procedure is as follows:

* For each category:
     * retrieves station information
     * for each station:
         * retrieves data_types
         * for each data_type:
             * recovers records for a period of time

For each record with period greater than 300 seconds, multiple records with period 300 serconds and consistent values are produced based on the data type (see above).

All records are then saved to an `output.csv` file with the following format:

```
data_type,timestamp,value
```

#### Transformation

The `to-numpy-data.py` file is executed as follows:

```
./run to_numpy
```

This script aggregates the records for temporal time-slots (ie: every 1800 seconds) using the configuration in `config.json` by creating the` labels.npy` and `features.npy` files that are used by the network for both training and to make live predictions.

In particular it limits the expected output (PM2.5) so that it has range [0-1].

The normalizations of the input data (features) are made by the loader for reasons explained later.


### Loading

The `loader.py` file is used to load previously produced data and applies normalization based on the scenario.

In particular, it can be used to:

- Extract the time series, dividing them into both training and validation sets. Training is used to train the network, validation to verify the accuracy of the model on data that the network has never seen. In particular, it performs the following steps:
    - normalizing the features of the training data so that each have an average value of 0 and a standard deviation of 1 (this is a best practice);
    - the original mean and standard deviation of the training data are saved and then applied to the test data.
- Extract the time series preceding the provided timestamp. It is used during the live "phase". In this case, the mean and standard deviation that are saved during the training are applied to the time series.

## Pipeline

#### Training

To train the network one can run the following commands:

```
./run download
./run to_numpy
./run train <epochs>
```

where `epochs` represents the number of training iterations of the network.

#### Live

For running the live application there are several scripts:

- start.sh: runs the application server (see below)
- update.sh: performs the batch download (of the last 10 days) and performs the time aggregations

The application can be run using the following script:

```
./run app
```

This script will run the docker container exposing the **5000** port. Docker sets up a `cron` job that performs an update as described above every day at 00:01. Here one can query the service by requesting up to 9 days of historical data.

The application server responds to the following routes:

- `/predict?date=yyyy-mm-dd`: returns a json with for the provided date
    - labels: historical data of PM2.5
    - outputs: the predicted data by the neural network 
    - timestamps: ordered list of timestamps matching the prediction
- `/predict?start=yyyy-mm-dd&end=yyyy-mm-dd`: returns a json similar to the one described above for the selected date range.

#### Files

We already provide the weights, means and stds (all in the weights folder) as a result of our training of the model so it is not needed to run the download, to_numpy and train steps to go live.
