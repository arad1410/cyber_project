import socket
import threading
import database
import pickle
import tqdm
import os
import Encryption_proj

FILE_LIST = {}
FILES = "server_files\\"
USER_FILE = "data.db"
FILE_DATABASE = "file_database.pickle"
BUFFER_SIZE = 4096
CLIENTS_SOCKET = {}  # global arg that has all the clients and there socket


class ClientHandler(threading.Thread):
    def __init__(self, address, sock):
        super(ClientHandler, self).__init__()
        global FILE_LIST, USER_FILE
        self.sock = sock
        self._name = address
        self.dict = database.SyncDataBase(USER_FILE)  # creates a dictionary with all the user name and password
        self.file_dict = database.SyncDataBase(FILE_DATABASE)  # creates a dictionary with all the files and their
        # client
        FILE_LIST = self.file_dict.dict.dict  # creates global arg so all te clients wii have the same file list
        self.rsa = Encryption_proj.RSACrypt()
        self.rsa.create_public_key()
        self.public_key = self.rsa.public_key
        self.aes = Encryption_proj.AESEncryption()
        self.key = None

    def run(self):
        self.sock.send(pickle.dumps(self.public_key))
        self.key = self.rsa.decode(self.sock.recv(1024))
        global FILE_LIST, CLIENTS_SOCKET
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
                self.dict = database.SyncDataBase(USER_FILE)
                self.dict.check(msg["user_name"])  # checks if the user name already exists
                if self.dict.answer:
                    print("here")
                    self.send_message("no")
                else:
                    self.dict.write(msg["user_name"], msg["user_password"])
                    print("arad")
                    self.send_message("good")
                    CLIENTS_SOCKET[msg["user_name"]] = (self.sock, self.key)
                    print(CLIENTS_SOCKET)
            elif msg["action"] == "c":  # checks if the action is to check if the password and user name that were
                # given are correct
                self.dict.check(msg["user_name"])
                if not self.dict.answer:
                    print("here3")
                    self.send_message("no")
                else:
                    self.dict.check_login(msg["user_name"], msg["user_password"])
                    print(self.dict.answer)
                    if self.dict.answer:
                        self.send_message("good")
                        CLIENTS_SOCKET[msg["user_name"]] = (self.sock, self.key)
                    else:
                        print("here2")
                        self.send_message("no")
            elif msg["action"] == "f":  # checks if the action is to upload a new file name
                self.file_dict.check(msg["file_name"])  # checks if the file name exists
                if self.file_dict.answer:
                    self.send_message("no")
                else:
                    self.file_dict.write(msg["file_name"], msg)
                    self.send_message("good")
                    print(self.file_dict.dict.dict)
                    FILE_LIST = self.file_dict.dict.dict
            elif msg["action"] == "s":  # checks if the action is to receive the file list
                print(FILE_LIST)
                self.send_message(FILE_LIST)
            elif msg["action"] == "u":  # checks if the action is to upload a file to the server
                self.send_message("start_sending")
                self.file_dict.write(msg["file_name"], msg)
                FILE_LIST = self.file_dict.dict.dict
                new_file = FILES + msg["file_name"].split("\\")[-1]
                progress = tqdm.tqdm(range(msg["file_size"]), f"Receiving {new_file}", unit="B", unit_scale=True,
                                     unit_divisor=1024)
                with open(new_file, "wb") as f:
                    data = self.sock.recv(BUFFER_SIZE)
                    while "done sending".encode() not in data:
                        bytes_read = self.aes.decrypt_aes(data, self.key)
                        f.write(bytes_read)
                        data = self.sock.recv(BUFFER_SIZE)
                    print(data)
                    data = data[0:-12]
                    print(data)
                    bytes_read = self.aes.decrypt_aes(data, self.key)
                    f.write(bytes_read)
                    print("done")
            elif msg["action"] == "fs":  # checks if the action receive a file from the server
                self.send_message(
                    str(os.path.getsize(FILES + msg["file_name"].split("\\")[-1])) + "$" + msg["file_name"].split("\\")[
                        -1])
                file = FILES + msg["file_name"].split("\\")[-1]
                progress = tqdm.tqdm(range(os.path.getsize(file)), f"Sending {file}", unit="B", unit_scale=True,
                                     unit_divisor=1024)
                with open(file, "rb") as f:
                    f = f.read()
                    f = self.aes.encrypt_aes(f, self.key)
                    f += "done sending".encode()
                    counter = 0
                    for _ in progress:
                        # read the bytes from the file
                        bytes_read = f[BUFFER_SIZE * counter:BUFFER_SIZE * (counter + 1)]
                        print(bytes_read)
                        if not bytes_read:
                            # file transmitting is done
                            print("done")
                            break
                        # we use sendall to assure transimission in
                        # busy networks
                        counter += 1
                        self.sock.sendall(bytes_read)
                        # update the progress bar
                        progress.update(len(bytes_read))
            elif msg["action"] == "sr":  # checks if the action is to receive a file from a specific client
                if msg["user_name"] in CLIENTS_SOCKET:  # checks if the client is around
                    if CLIENTS_SOCKET[msg["user_name"]][0] == self.sock:
                        self.send_message("your file")
                    else:
                        print(CLIENTS_SOCKET[msg["user_name"]][0])
                        self.send_message("asked the client")
                        CLIENTS_SOCKET[msg["user_name"]][0].send(
                            self.aes.encrypt_aes(pickle.dumps("@" + msg["file_name"]),
                                                 CLIENTS_SOCKET[msg["user_name"]][1]))  # sends the
                        # client that you want his file
                else:
                    self.send_message("user not around")
            elif msg["action"] == "wc":  # checks if the action is to receive a file from a specific client
                if msg["user_name"] in CLIENTS_SOCKET:  # checks if the client is around
                    if CLIENTS_SOCKET[msg["user_name"]][0] == self.sock:
                        self.send_message("your file")
                    else:
                        print(CLIENTS_SOCKET[msg["user_name"]][0])
                        self.send_message("asked the client")
                        CLIENTS_SOCKET[msg["user_name"]][0].send(
                            self.aes.encrypt_aes(pickle.dumps("@" + msg["file_name"]),
                                                 CLIENTS_SOCKET[msg["user_name"]][1]))  # sends the
                        # client that you want his file

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
