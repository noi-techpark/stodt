import json
import os
from datetime import datetime
from os import environ
from subprocess import Popen

from flask import Flask, request, jsonify
from flask_cors import CORS
from modules.predict import Predicter

# Configuration
from modules.utilities import time_frames_from

with open('./config.json') as configfile:
    config = json.loads("".join(configfile.readlines()))
neural_network_config = config["neural-network"]

port = int(environ.get("PORT", 5000))
app = Flask(__name__, static_url_path='', static_folder='www')
CORS(app)

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/predict')
def predict():
    datestring = request.args.get("date")

    if datestring is not None:
        date = datetime.strptime(datestring, '%Y-%m-%d')
    else:
        date = datetime.now()

    predicter = Predicter(neural_network_config)
    labels, outputs, timestamps = _predict_dates([date], predicter)

    return jsonify(dict(timestamps=timestamps,
                        labels=labels,
                        outputs=outputs))


@app.route('/history')
def history():
    end = datetime.strptime(request.args.get("end"), '%Y-%m-%d')
    start = datetime.strptime(request.args.get("start"), '%Y-%m-%d')
    days = time_frames_from(start, end, 1)

    predicter = Predicter(neural_network_config)
    labels, outputs, timestamps = _predict_dates(days, predicter)

    return jsonify(dict(timestamps=timestamps,
                        labels=labels,
                        outputs=outputs))


@app.route("/manual-update")
def update():
    if os.path.exists("/tmp/update-running"):
        return "Already updating..."
    Popen(["bash", "/app/update.sh"])
    return "Update started."


def _predict_dates(days, predicter):
    timestamps, labels, outputs = predicter.predict(days)
    timestamps = [datetime.fromtimestamp(timestamp).isoformat() for timestamp in timestamps]

    return labels, outputs, timestamps


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=port)
