# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import json
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt

def dateparse(time_in_ms):
    return datetime.datetime.fromtimestamp(time_in_ms / 1000.0)

def fillHoles(values, indexes, reduces_indexes):
    mask = np.searchsorted(indexes, reduces_indexes)
    filled_values = np.full([indexes.size, 1], np.nan)
    filled_values[mask] = values
    filled_values = np.where(np.isnan(filled_values), np.ma.array(filled_values, mask=np.isnan(filled_values)).mean(),filled_values)
    return filled_values

#  Loads configuration
with open('./config.json') as configfile:
    config = json.loads("".join(configfile.readlines()))
time_frame_size = str(config["neural-network"]["time_frame_size"]) + "s"
target_data_type = config["neural-network"]["target_data_type"]
target_data_type_max_value = config["neural-network"]["target_data_type_max_value"]
data_dir = config["data_dir"]

# Loads records from csv file
matrix = pd.read_csv(data_dir + '/output.csv', header=None, names=["data_type", "timestamp", "value"])
matrix['timestamp'] = matrix['timestamp'].apply(dateparse)

# Extract all valid time ranges
time_ranges = matrix.groupby(pd.Grouper(key='timestamp', freq=time_frame_size)).mean().reset_index()['timestamp'].to_numpy()

# Extract data types
data_types = []
for category in config["categories"]:
    for data_type in category["allowed_data_types"]:
        data_types.append(data_type["name"])

# Prepare for plot
max_time = matrix["timestamp"].max().strftime("%Y-%m-%d")
min_time = matrix["timestamp"].min().strftime("%Y-%m-%d")
figure, subplot = plt.subplots(len(data_types), 1, constrained_layout=True)

figure.suptitle('Records by timeframe (' + time_frame_size + ') from ' + min_time + " to " + max_time)
figure.set_figheight(30)
figure.set_figwidth(30)

ts = (time_ranges - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')

label_array = np.reshape(ts, (-1, 1))
feature_matrix = np.reshape(ts, (-1, 1))
for data_type in data_types:
    # Filter by data type
    data_type_records = matrix.loc[matrix["data_type"] == data_type]

    # Ignore the data_type column
    data_type_records = data_type_records.loc[:, "timestamp":]

    # Group by timeslots and count the records
    record_number_by_timeframe = data_type_records.groupby(pd.Grouper(key='timestamp', freq=time_frame_size)).mean()

    # Extract time ranges for data_type
    data_type_time_ranges = record_number_by_timeframe.reset_index()['timestamp'].to_numpy()

    # Prepare axises' values
    y = record_number_by_timeframe.to_numpy()
    x = time_ranges

    # Fill the holes in detections
    y = fillHoles(y, time_ranges, data_type_time_ranges)

    # Fill features and labels arrays
    if data_type == target_data_type:
        y[y > target_data_type_max_value] = target_data_type_max_value
        label_array = np.hstack((label_array, y / target_data_type_max_value))
    feature_matrix = np.hstack((feature_matrix, y))

    # Subplot
    index = data_types.index(data_type)
    subplot[index].plot(x, y)
    subplot[index].set_title(data_type)

# Save the plot
plt.savefig(data_dir + '/plot.svg', format='svg', dpi=2400)

# Save feature matrix to file
np.save(data_dir + "/features", feature_matrix)
np.save(data_dir + "/labels", label_array)
