import socket
import threading
import database
import pickle
import tqdm
import os
import Encryption_proj

DATABASE = "data.db"  # holds all the clients
BUFFER_SIZE = 4096
CLIENTS_SOCKET = {}  # global arg that has all the clients and there socket
All_CLIENTS_NAMES = []  # names of all the clients


class ClientHandler(threading.Thread):
    def __init__(self, address, sock):
        super(ClientHandler, self).__init__()
        global DATABASE
        self.sock = sock
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
        global  CLIENTS_SOCKET, All_CLIENTS_NAMES
        on = True
        while on:
            try:
                msg = pickle.loads(self.aes.decrypt_aes(self.sock.recv(1024), self.key))
                print(msg)
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
                else:
                    self.dict.write(msg["user_name"], msg["user_password"])
                    self.send_message("good")
                    clients = "& " + " ".join(All_CLIENTS_NAMES)
                    self.send_message(clients)
                    print(clients)
                    All_CLIENTS_NAMES.append(msg["user_name"])
                    clients = "& " + " ".join(All_CLIENTS_NAMES)
                    for client in CLIENTS_SOCKET:
                        CLIENTS_SOCKET[client][0].send(
                            self.aes.encrypt_aes(pickle.dumps(clients),
                                                 CLIENTS_SOCKET[client][1]))
                    CLIENTS_SOCKET[msg["user_name"]] = (self.sock, self.key)
                    print(CLIENTS_SOCKET)
            elif msg["action"] == "c":  # checks if the action is to check if the password and user name that were
                # given are correct
                self.dict.check(msg["user_name"])
                if not self.dict.answer:
                    self.send_message("no")
                else:
                    self.dict.check_login(msg["user_name"], msg["user_password"])
                    print(self.dict.answer)
                    if self.dict.answer:
                        self.send_message("good")
                        clients = "& " + " ".join(All_CLIENTS_NAMES)
                        self.send_message(clients)
                        print(clients)
                        All_CLIENTS_NAMES.append(msg["user_name"])
                        clients = "& " + " ".join(All_CLIENTS_NAMES)
                        for client in CLIENTS_SOCKET:
                            print()
                            CLIENTS_SOCKET[client][0].send(
                                self.aes.encrypt_aes(pickle.dumps(clients),
                                                     CLIENTS_SOCKET[client][1]))
                        CLIENTS_SOCKET[msg["user_name"]] = (self.sock, self.key)
                    else:
                        self.send_message("no")
            elif msg["action"] == "wc":  # checks if the action is to receive a file from a specific client
                if msg["user_name"] in CLIENTS_SOCKET:  # checks if the client is around
                    if CLIENTS_SOCKET[msg["user_name"]][0] == self.sock:
                        self.send_message("your file")
                    else:
                        print(CLIENTS_SOCKET[msg["user_name"]][0])
                        CLIENTS_SOCKET[msg["user_name"]][0].send(
                            self.aes.encrypt_aes(pickle.dumps("@ " + msg["my_user_name"]),
                                                 CLIENTS_SOCKET[msg["user_name"]][1]))  # sends the
                        # client that you want his file
            elif msg["action"] == "yes" or msg["action"] == "no":
                print("araddddd")
                CLIENTS_SOCKET[msg["user_name"]][0].send(
                    self.aes.encrypt_aes(pickle.dumps(msg["action"]),
                                         CLIENTS_SOCKET[msg["user_name"]][1]))
            elif msg["action"] == "work":
                CLIENTS_SOCKET[msg["user_name"]][0].send(
                    self.aes.encrypt_aes(pickle.dumps("lets start" + msg["file_name"]),
                                         CLIENTS_SOCKET[msg["user_name"]][1]))

    def send_message(self, msg):
        self.sock.send(self.aes.encrypt_aes(pickle.dumps(msg), self.key))


class Server(object):
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
