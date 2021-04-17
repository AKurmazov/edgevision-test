import json
import datetime
import copy
import time
import socket

from flask import Flask, Response, request
from apscheduler.schedulers.background import BackgroundScheduler


# TCP connection data
HOST = "manipulator"
PORT = 5002


# Initialize Flask app
app = Flask(__name__)


# Initial conditions
semaphore = False
signals = []


def request_manipulator():
    global signals, semaphore

    # Use the concept of semaphore so that not to let the
    # list of signals be changed while modifying
    semaphore = True
    _signals = copy.copy(signals)
    signals = []
    semaphore = False

    _sum = sum(_signals)
    _len = len(_signals)

    # The decision whether the manipulator gets "up" or "down"
    # signal is based on the mean of sensors' payloads
    status = "up" if _len and _sum / _len >= 10.0 else "down"
    timestamp = datetime.datetime.now().strftime("%Y%m%dT%H%M")

    man_signal = f"Status changed to {status.upper()} at {timestamp}"
    with open("logs.txt", "a") as out_file:
        out_file.write(f"{man_signal}\n")

    # Initialize TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Send signal to manipulator
    sock.connect((HOST, PORT))
    sock.send(man_signal.encode('utf-8'))

    # Close TCP socket
    sock.close()


@app.route("/", methods=["POST"])
def controller():
    global signals
    
    if request.method == "POST":
        data = request.json

        while semaphore:
            print("Waiting for semaphore to go down...")
        signals.extend(list(map(lambda item: int(item["payload"]), data)))

        return Response(status=200)


if __name__ == "__main__":
    # Initialize scheduler
    scheduler = BackgroundScheduler(daemon=True)

    # Set up periodic job
    scheduler.add_job(request_manipulator, "interval", seconds=5, max_instances=10)
    scheduler.start()

    # Run application at localhost
    app.run(host="0.0.0.0", threaded=True)
