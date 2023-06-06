# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import math
import numpy as np

class Loader:
    def __init__(self, config):
        self.batch_size = config["batch_size"]
        self.data_dir = config["weight_dir"]
        self.time_series_length = config["time_series_length"]
        self.dataset_splits = config["dataset_splits"]
        self.lookup_window = config["lookup_window"]
        self.train_consecutive_batches = config["train_consecutive_batches"]
        self.validation_consecutive_batches = config["validation_consecutive_batches"]
        self.training_percentage = (config["train_consecutive_batches"]) / (config["train_consecutive_batches"] + config["validation_consecutive_batches"])

    def timeshifted_timeseries(self, X, Y, batch_start, number):
        timeseries_X = []
        timeseries_Y = []

        for timeseries_index in range(batch_start, batch_start + number):
            timeseries_end = timeseries_index + self.time_series_length

            timeseries_X.append(X[timeseries_index:timeseries_end])
            timeseries_Y.append(Y[timeseries_end:timeseries_end + self.lookup_window])

        timeseries_X = np.reshape(np.stack(timeseries_X), (-1, self.time_series_length, X.shape[1]))
        timeseries_Y = np.reshape(np.stack(timeseries_Y), (-1, self.lookup_window, Y.shape[1]))

        return timeseries_X, timeseries_Y

    def a_timeseries_before(self, X, Y, timestamp, time_frame_size):
        timeslot = X[1, 0] - X[0, 0]
        if X[-1, 0] + timeslot < timestamp:
            raise RuntimeError("Invalid date")
        if X[0, 0] > timestamp - timeslot * self.time_series_length:
            raise RuntimeError("Invalid date")

        intermediate_point = np.argwhere(X[:, 0] <= timestamp)[-1, 0]

        end = intermediate_point + self.lookup_window
        start = intermediate_point - self.time_series_length

        timeseries_X = X[start:intermediate_point]

        timeseries_Y = np.zeros((self.lookup_window, Y.shape[1]))
        timeseries_Y[:] = np.nan
        timeseries_Y[:, 0] = np.arange(timestamp, timestamp + self.lookup_window * time_frame_size, time_frame_size)

        window_ = Y[intermediate_point:end]
        timeseries_Y[:window_.shape[0], :window_.shape[1]] = window_

        train_mean = np.load(self.data_dir + "/means.npy")
        train_std = np.load(self.data_dir + "/stds.npy")

        timeseries_X[:, 1:] = (timeseries_X[:, 1:] - train_mean) / train_std

        return np.expand_dims(timeseries_X, 0), np.expand_dims(timeseries_Y, 0)

    def load(self, X, Y):
        split_size = math.floor(X.shape[0] / self.dataset_splits)
        training_X = []
        training_Y = []
        validation_X = []
        validation_Y = []
        for i in np.arange(0, split_size * self.dataset_splits, split_size):
            training_records = int(split_size * self.training_percentage)
            validation_records = int(split_size * (1 - self.training_percentage))

            training_timeseries = training_records - self.time_series_length + 1
            validation_timeseries = validation_records - self.time_series_length - self.lookup_window + 1

            training_X_B, training_Y_B = self.timeshifted_timeseries(X, Y, i, training_timeseries)
            validation_X_B, validation_Y_B = self.timeshifted_timeseries(X, Y, i + training_records, validation_timeseries)

            training_X.append(training_X_B)
            training_Y.append(training_Y_B)
            validation_X.append(validation_X_B)
            validation_Y.append(validation_Y_B)

        training_X = np.vstack(training_X)
        training_Y = np.vstack(training_Y)
        validation_X = np.vstack(validation_X)
        validation_Y = np.vstack(validation_Y)

        train_limit = math.floor(training_X.shape[0] / self.batch_size) * self.batch_size
        validation_limit = math.floor(validation_X.shape[0] / self.batch_size) * self.batch_size

        train_mean = np.expand_dims(np.mean(training_X[:, :, 1:], (0, 1)), 0)
        train_std = np.expand_dims(np.std(training_X[:, :, 1:], (0, 1)), 0)

        np.save(self.data_dir + "/means", train_mean)
        np.save(self.data_dir + "/stds", train_std)

        training_X[:, :, 1:] = (training_X[:, :, 1:] - train_mean) / train_std
        validation_X[:, :, 1:] = (validation_X[:, :, 1:] - train_mean) / train_std

        return training_X[:train_limit], training_Y[:train_limit], validation_X[:validation_limit], validation_Y[:validation_limit]