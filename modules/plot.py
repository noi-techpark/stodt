from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np


class Plot:
    def __init__(self, data_dir, config):
        self.data_dir = data_dir
        self.lookup_window = config["lookup_window"]

    def shuffleArrays(self, array1, array2):
        mask = np.random.permutation(len(array1))
        return array1[mask], array2[mask]

    def save_plot(self, plt, outputIO):
        plt.savefig(outputIO)

    def datetime_from(self, array):
        return np.array([datetime.fromtimestamp(x) for x in array[:, 0]], dtype=np.datetime64)

    def plot(self, outputIO, labels, outputs, timestamps):
        subrange = np.arange(1, 300)  # HARD-CODED

        labels_new = np.reshape(labels[0], (-1, 1))
        outputs_new = np.reshape(outputs[0], (-1, 1))
        timestamps_new = np.reshape(timestamps[0], (-1, 1))

        for i in subrange:
            last_label = np.reshape(labels[i], (-1, 1))[-1]
            np.append(labels_new, last_label)

            last_output = np.reshape(outputs[i], (-1, 1))[-1]
            np.append(outputs_new, last_output)

            last_timestamp = np.reshape(timestamps[i], (-1, 1))[-1]
            np.append(timestamps_new, last_timestamp)

        plt.figure(figsize=(30, 10))

        timestamps_new = self.datetime_from(timestamps_new)

        plt.plot(timestamps_new, outputs_new)
        plt.plot(timestamps_new, labels_new)
        self.save_plot(plt, outputIO)

    def plot_one(self, outputIO, labels, outputs, timestamps):
        labels_new = np.reshape(labels, (-1, 1))
        outputs_new = np.reshape(outputs, (-1, 1))
        timestamps_new = np.reshape(timestamps, (-1,1))
        timestamps_new = self.datetime_from(timestamps_new)

        plt.figure(figsize=(30, 10))

        plt.plot(timestamps_new, outputs_new)
        plt.plot(timestamps_new, labels_new)
        self.save_plot(plt, outputIO)

    def plot_without_timestamps(self, outputIO, labels, outputs):
        subrange = np.arange(1, 300)  # HARD-CODED

        labels_new = np.reshape(labels[0], (-1, 1))
        outputs_new = np.reshape(outputs[0], (-1, 1))

        for i in subrange:
            last_label = np.reshape(labels[i], (-1, 1))[-1]
            np.append(labels_new, last_label)

            last_output = np.reshape(outputs[i], (-1, 1))[-1]
            np.append(outputs_new, last_output)

        plt.figure(figsize=(30, 10))

        plt.plot(outputs_new)
        plt.plot(labels_new)
        self.save_plot(plt, outputIO)