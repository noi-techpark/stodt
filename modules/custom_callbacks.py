from tensorflow.keras import callbacks
from datetime import datetime

class PlotCallback(callbacks.Callback):
    def __init__(self, model, plot, file, x, y):
        self.plot = plot
        self.model = model
        self.file = file
        self.x = x
        self.y = y

    def on_epoch_end(self, epochs, debug_log=False):
        self.plot.plot_without_timestamps(self.file, self.y, self.model.predict(self.x))

class Tensorboard(callbacks.TensorBoard):
    def __init__(self, data_dir):
        log_dir = data_dir + "/board/" + datetime.now().strftime("%Y%m%d-%H%M%S")
        super(Tensorboard, self).__init__(log_dir=log_dir, histogram_freq=1)

class EarlyStop(callbacks.EarlyStopping):
    def __init__(self, patience):
        super(EarlyStop, self).__init__(monitor="val_loss", mode="min", restore_best_weights=True, verbose=1, patience=patience)
