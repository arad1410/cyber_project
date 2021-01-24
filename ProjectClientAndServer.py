import socket
import pickle
import tqdm
import os
import Encryption_proj

BUFFER_SIZE = 4096


class Client(object):

    def __init__(self):
        self.my_socket = socket.socket()
        self.server_ip = "127.0.0.1"
        self.server_port = 8888
        self.answer = None
        self.run = True
        self.aes = Encryption_proj.AESEncryption()
        self.rsa = Encryption_proj.RSACrypt()
        self.key = self.aes.key
        self.file = None
        self.sending = None
        self.start_connection()

    def start_connection(self):
        while self.run:  # waits until the connection was successful
            try:
                self.my_socket.connect((self.server_ip, self.server_port))
                self.run = False
            except socket.error:
                pass
        self.rsa.public_key = pickle.loads(self.my_socket.recv(1024))
        self.my_socket.send(self.rsa.encrypt(self.key))
        self.rcv_file()

    def rcv_file(self):
        print("start")
        self.answer = pickle.loads(self.my_socket.recv(1024))
        self.answer = self.answer.split(" ", 1)
        self.answer[1] = self.answer[1].split("\\")[-1]
        progress = tqdm.tqdm(range(int(self.answer[0])), f"Receiving {self.answer[1]}", unit="B", unit_scale=True,
                             unit_divisor=1024)
        self.file = self.answer[1]
        with open(self.answer[1], "wb") as f:
            data = self.my_socket.recv(BUFFER_SIZE)
            while "done sending".encode() not in data:
                bytes_read = self.aes.decrypt_aes(data, self.key)
                f.write(bytes_read)
                data = self.my_socket.recv(BUFFER_SIZE)
            print(data)
            data = data[0:-12]
            print(data)
            bytes_read = self.aes.decrypt_aes(data, self.key)
            f.write(bytes_read)
            print("done")
            self.sending = True
        self.file = self.answer[1]
        return

    def rcv(self):
        return self.aes.decrypt_aes(self.my_socket.recv(1024), self.key)

    def send(self, data):
        self.my_socket.send(self.aes.encrypt_aes(data, self.key))


class Server(object):
    def __init__(self, file):
        self.sock = socket.socket()
        self.port = 8888
        self.file = file
        self.client_sock = None
        self.rsa = Encryption_proj.RSACrypt()
        self.rsa.create_public_key()
        self.public_key = self.rsa.public_key
        self.aes = Encryption_proj.AESEncryption()
        self.key = None
        self.start_connection()

    def start_connection(self):
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.listen(1)
        self.client_sock, address = self.sock.accept()
        self.client_sock.send(pickle.dumps(self.public_key))
        self.key = self.rsa.decode(self.client_sock.recv(1024))
        self.send_file(self.file)

    def rcv(self):
        return self.aes.decrypt_aes(self.client_sock.recv(1024), self.key)

    def send(self, data):
        self.client_sock.send(self.aes.encrypt_aes(data, self.key))

    def send_file(self, file):
        print("start")
        self.client_sock.send(pickle.dumps(str(os.path.getsize(file)) + " " + file))
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
                self.client_sock.sendall(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))
