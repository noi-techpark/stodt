from __future__ import absolute_import, division, print_function, unicode_literals

import json
import math
import numpy as np

from modules.loader import Loader
from modules.neural import Neural

# Configuration
with open('./config.json') as configfile:
    config = json.loads("".join(configfile.readlines()))
data_dir = config["data_dir"]

neural_network_config = config["neural-network"]
weight_dir = neural_network_config["weight_dir"]

# Utility classes
loader = Loader(neural_network_config)

def to_python_list(array):
    array = np.reshape(array, (-1))
    return [np.asscalar(a) if not math.isnan(np.asscalar(a)) else None for a in np.array(array)]

class Predicter:
    def __init__(self, config):
        self.time_frame_size = config["time_frame_size"]

    def predict(self, dates):
        # Load stuff
        numpy_features = np.load(data_dir + "/features.npy")
        numpy_labels = np.load(data_dir + "/labels.npy")

        features = []
        labels = []
        for date in dates:
            tmpX, tmpY = loader.a_timeseries_before(numpy_features, numpy_labels, date.timestamp(), self.time_frame_size)
            features.append(tmpX)
            labels.append(tmpY)
        features, labels = np.vstack(features), np.vstack(labels)
        
        timestamps = np.expand_dims(labels[:, :, 0], 2)
        features, labels = features[:, :, 1:], labels[:, :, 1:]

        # Evaluation stuff
        neural = Neural(features.shape[2], neural_network_config)
        neural.load(weight_dir + "/weights")

        outputs = np.reshape(neural.predict(features), labels.shape)

        return to_python_list(timestamps), to_python_list(labels), to_python_list(outputs)
