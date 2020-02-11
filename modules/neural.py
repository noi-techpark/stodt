from __future__ import absolute_import, division, print_function, unicode_literals

from tensorflow.keras import layers, models, optimizers, backend, activations


def rmse(labels, predicted):
    return backend.sqrt(backend.mean(backend.square(predicted - labels)))


class Neural:

    def __init__(self, input_dim, config):
        self.batch_size = config["batch_size"]
        self.time_series_length = config["time_series_length"]
        self.units = config["units"]
        self.custom_callbacks = []

        model = models.Sequential()
        model.add(layers.GaussianNoise(0.1))
        model.add(layers.GRU(self.units,
                             return_sequences=True,
                             recurrent_activation=activations.tanh,
                             batch_input_shape=(self.batch_size, self.time_series_length, input_dim)))
        model.add(layers.Dropout(0.2))
        model.add(layers.TimeDistributed(layers.Dense(1, activation=activations.sigmoid)))

        model.compile(loss=rmse,
                      optimizer='adam')

        self.model = model

    def set_callbacks(self, *callbacks):
        self.custom_callbacks = list(callbacks)

    def fit(self, epochs, x_train, y_train, x_test, y_test):
        self.model.fit(x_train, y_train,
                       validation_data=(x_test, y_test),
                       batch_size=self.batch_size,
                       epochs=epochs,
                       callbacks=self.custom_callbacks,
                       shuffle=False)

    def predict(self, X):
        return self.model.predict(X)

    def load(self, path):
        self.model.load_weights(path)

    def save(self, path):
        self.model.save_weights(path)
