import socket
import threading
import database
import pickle
import Encryption_proj

DATABASE = "data.db"  # holds all the clients
BUFFER_SIZE = 4096
CLIENTS_SOCKET = {}  # global arg that has all the clients and there socket
All_CLIENTS_NAMES = []  # names of all the clients


class ClientHandler(threading.Thread):
    # in charge of accepting and talking to many clients at the same time with threads
    def __init__(self, address, sock):
        super(ClientHandler, self).__init__()
        global DATABASE
        self.sock = sock  # the socket of each client to talk on
        self._name = address
        self.dict = database.SyncDataBase(DATABASE)  # creates a dictionary with all the user name and password
        # client
        self.rsa = Encryption_proj.RSACrypt()
        self.rsa.create_public_key()
        self.public_key = self.rsa.public_key
        self.aes = Encryption_proj.AESEncryption()
        self.key = None

    def run(self):
        self.sock.send(pickle.dumps(self.public_key))
        self.key = self.rsa.decode(self.sock.recv(1024))
        global CLIENTS_SOCKET, All_CLIENTS_NAMES
        on = True
        while on:
            try:
                msg = pickle.loads(self.aes.decrypt_aes(self.sock.recv(1024), self.key))
            except EOFError:
                break
            if msg == "close connection":
                for key in CLIENTS_SOCKET:  # runs until it finds the correct client to delete their socket
                    if CLIENTS_SOCKET[key] == self.sock:
                        del CLIENTS_SOCKET[key]
                        break
                on = False
                self.send_message("close client")
                self.sock.close()
            elif msg["action"] == "w":  # checks if the action is to write a new client that wants to join
                self.dict = database.SyncDataBase(DATABASE)
                self.dict.check(msg["user_name"])  # checks if the user name already exists
                if self.dict.answer:
                    self.send_message("no")
                else:  # if it doesnt it adds it to the database
                    self.dict.write(msg["user_name"], msg["user_password"])
                    self.send_message("good")
                    clients = "& " + " ".join(All_CLIENTS_NAMES)
                    self.send_message(clients)  # send the list of all the clients to the client so he will
                    # be able to choose who to work with
                    All_CLIENTS_NAMES.append(msg["user_name"])
                    clients = "& " + " ".join(All_CLIENTS_NAMES)
                    for client in CLIENTS_SOCKET:
                        CLIENTS_SOCKET[client][0].send(
                            self.aes.encrypt_aes(pickle.dumps(clients),
                                                 CLIENTS_SOCKET[client][1]))  # sends all the clients that are connected
                        # the list of all the other clients that are connected to the server
                    CLIENTS_SOCKET[msg["user_name"]] = (self.sock, self.key)
            elif msg["action"] == "c":  # checks if the action is to check if the password and user name that were
                # given are correct
                self.dict.check(msg["user_name"])
                if not self.dict.answer:
                    self.send_message("no")
                else:  # means that the client was successful in login in
                    self.dict.check_login(msg["user_name"], msg["user_password"])
                    if self.dict.answer:
                        self.send_message("good")  # send that the login was successful
                        clients = "& " + " ".join(All_CLIENTS_NAMES)
                        self.send_message(clients)  # send the list of all the clients to the client so he will
                        # be able to choose who to work with
                        All_CLIENTS_NAMES.append(msg["user_name"])
                        clients = "& " + " ".join(All_CLIENTS_NAMES)
                        for client in CLIENTS_SOCKET:
                            CLIENTS_SOCKET[client][0].send(
                                self.aes.encrypt_aes(pickle.dumps(clients),
                                                     CLIENTS_SOCKET[client][1]))  # sends all the clients that are
                            # connected the list of all the other clients that are connected to the server
                        CLIENTS_SOCKET[msg["user_name"]] = (self.sock, self.key)
                    else:
                        self.send_message("no")
            elif msg["action"] == "wc":  # checks if the action is to receive a file from a specific client
                if msg["user_name"] in CLIENTS_SOCKET:  # checks if the client is around
                    if CLIENTS_SOCKET[msg["user_name"]][0] == self.sock:
                        self.send_message("your file")
                    else:
                        CLIENTS_SOCKET[msg["user_name"]][0].send(
                            self.aes.encrypt_aes(pickle.dumps("@ " + msg["my_user_name"]),
                                                 CLIENTS_SOCKET[msg["user_name"]][1]))  # sends the
                        # client that you want his file
            elif msg["action"] == "yes" or msg["action"] == "no":  # means that the other client sent his response to
                # the request of the file sync
                CLIENTS_SOCKET[msg["user_name"]][0].send(
                    self.aes.encrypt_aes(pickle.dumps(msg["action"]),
                                         CLIENTS_SOCKET[msg["user_name"]][1]))  # sends the client the response of the
                # other client
            elif msg["action"] == "work":  # means that they can start to work together on the file
                CLIENTS_SOCKET[msg["user_name"]][0].send(
                    self.aes.encrypt_aes(pickle.dumps("lets start" + msg["file_name"]),
                                         CLIENTS_SOCKET[msg["user_name"]][1]))

    def send_message(self, msg):
        self.sock.send(self.aes.encrypt_aes(pickle.dumps(msg), self.key))


class Server(object):
    # starts the server and
    def __init__(self):
        self.sock = socket.socket()
        self.port = 8080

    def listen(self):
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.listen(10)

    def accept(self):
        return self.sock.accept()


def main():
    server = Server()
    server.listen()
    while True:
        sock, address = server.accept()
        client_hand = ClientHandler(address, sock)
        client_hand.start()


if __name__ == "__main__":
    main()
