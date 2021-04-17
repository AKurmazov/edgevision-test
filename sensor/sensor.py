import random
import datetime
import time
import requests
import json


CONTROLLER_URL = "http://controller:5000"
MESSAGES_PER_SECOND = 300


def request_controller(session, payload):
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    try:
        response = session.post(CONTROLLER_URL, data=json.dumps(payload), headers=headers)
    except:
        pass


def generate_message():
    return {"datetime": datetime.datetime.now().strftime("%Y%m%dT%H%M"),
            "payload": random.randint(0, 20)}


def main():
    with requests.Session() as session:
        session.trust_env = False
        while True:
            was = time.time()
            data = []
            for _ in range(MESSAGES_PER_SECOND):
                data.append(generate_message())
            request_controller(session, data)
            print(time.time() - was)

            time.sleep(1)


if __name__ == "__main__":
    main()
