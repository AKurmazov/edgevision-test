import socket


# TCP socket data
HOST = socket.gethostname()
PORT = 5002


def init_socket():
    # Initialize TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(1)
    return sock


def log_signal(signal):
    # Log status change to the logging file
    with open("manipulator.log", "a") as out_file:
        out_file.write(f"{signal}\n")


def listen_to_controller(sock):
    while True:
        connection, address = sock.accept()

        signal = ""
        while True:
            data = connection.recv(128)
            if not data:
                break
            signal += data.decode("utf-8") 
        log_signal(signal)

        connection.close()


if __name__ == "__main__":
    sock = init_socket()
    listen_to_controller(sock)
