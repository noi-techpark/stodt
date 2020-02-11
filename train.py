from __future__ import absolute_import, division, print_function, unicode_literals

import json
import sys

import numpy as np

from modules.loader import Loader
from modules.neural import Neural
from modules.plot import Plot
from modules.custom_callbacks import Tensorboard, EarlyStop, PlotCallback

# Configuration
with open('./config.json') as configfile:
    config = json.loads("".join(configfile.readlines()))
data_dir = config["data_dir"]

neural_network_config = config["neural-network"]
reload_weights = neural_network_config["reload_weights"]

weight_dir = neural_network_config["weight_dir"]

if len(sys.argv) > 1:
    epochs = int(sys.argv[1])
else:
    epochs = neural_network_config["epochs"]

# Utility classes
loader = Loader(neural_network_config)

# Load stuff
X = np.load(data_dir + "/features.npy")
Y = np.load(data_dir + "/labels.npy")

# Training stuff
x_train, y_train, x_test, y_test = loader.load(X, Y)
x_train, y_train, x_test, y_test = x_train[:,:,1:], y_train[:,:,1:], x_test[:,:,1:], y_test[:,:,1:]

input_dim = x_train.shape[2]

neural = Neural(input_dim, neural_network_config)
neural.set_callbacks(EarlyStop(5))
if reload_weights:
    neural.load(weight_dir + "/weights")
neural.fit(epochs, x_train, y_train, x_test, y_test)

neural.save(weight_dir + "/weights")