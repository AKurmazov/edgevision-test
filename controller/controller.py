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
sensors_data = []


def request_manipulator():
    global sensors_data, semaphore

    # Use the concept of semaphore so that not to let the
    # list of sensors' data be changed while modifying
    while semaphore:
        pass  # Waiting for semaphore to go down...
    
    semaphore = True
    _sensors_data = copy.copy(sensors_data)
    sensors_data = []
    semaphore = False

    _sum = sum(_sensors_data)
    _len = len(_sensors_data)

    # The decision whether the manipulator gets "up" or "down"
    # signal is based on the mean of sensors' payloads
    status = "up" if _len and _sum / _len >= 10.0 else "down"
    timestamp = datetime.datetime.now().strftime("%Y%m%dT%H%M")
    signal = f"Status changed to {status.upper()} at {timestamp}"

    # Log decision to the logging file
    with open("controller.log", "a") as out_file:
        out_file.write(f"{signal}\n")

    # Initialize TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Send signal to manipulator
    sock.connect((HOST, PORT))
    sock.send(signal.encode('utf-8'))

    # Close TCP socket
    sock.close()


@app.route("/", methods=["POST"])
def controller():
    global sensors_data, semaphore

    if request.method == "POST":
        data = request.json

        # Similar to the request_manipulator code, use semaphore
        while semaphore:
            pass  # Waiting for semaphore to go down...

        semaphore = True
        sensors_data.extend(list(map(lambda item: int(item["payload"]), data)))
        semaphore = False

        return Response(status=200)


if __name__ == "__main__":
    # Initialize scheduler
    scheduler = BackgroundScheduler(daemon=True)

    # Set up periodic job
    scheduler.add_job(request_manipulator, "interval", seconds=5, max_instances=10)
    scheduler.start()

    # Run application at localhost
    app.run(host="0.0.0.0", threaded=True)
