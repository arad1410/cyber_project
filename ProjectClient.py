import socket
import pickle
import tqdm
import os
import Encryption_proj

BUFFER_SIZE = 4096


class Client(object):

    def __init__(self):
        self.my_socket = socket.socket()
        self.server_ip = "172.16.1.9"
        self.server_port = 8080
        self.answer = None
        self.aes = Encryption_proj.AESEncryption()
        self.rsa = Encryption_proj.RSACrypt()
        self.key = self.aes.key

    def start_connection(self):
        self.my_socket.connect((self.server_ip, self.server_port))
        self.rsa.public_key = pickle.loads(self.my_socket.recv(1024))
        self.my_socket.send(self.rsa.encrypt(self.key))

    def rcv_message(self):
        try:
            self.answer = pickle.loads(self.aes.decrypt_aes(self.my_socket.recv(1024), self.key))
            print(self.answer)
        except EOFError:
            pass
        if "$" in self.answer:  # if $ is in a message from the server that means im about to receive a file from the
            # server
            self.rcv_file()

    def send_message(self, msg):
        print(self.aes.encrypt_aes(pickle.dumps(msg), self.key))
        self.my_socket.send(self.aes.encrypt_aes(pickle.dumps(msg), self.key))
