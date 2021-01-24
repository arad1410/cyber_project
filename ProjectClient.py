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

    def rcv_file(self):
        self.answer = self.answer.split("$")
        progress = tqdm.tqdm(range(int(self.answer[0])), f"Receiving {self.answer[1]}", unit="B", unit_scale=True,
                             unit_divisor=1024)
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

    def send_file(self, file):
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
                self.my_socket.sendall(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))

    def send_message(self, msg):
        print(self.aes.encrypt_aes(pickle.dumps(msg), self.key))
        self.my_socket.send(self.aes.encrypt_aes(pickle.dumps(msg), self.key))
