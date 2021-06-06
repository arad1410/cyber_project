import socket
import pickle
import tqdm
import os
import Encryption_proj

BUFFER_SIZE = 4096


class ClientP2P(object):
    # creates the p2p client and talks to the client on the socket
    def __init__(self):
        self.my_socket = socket.socket()  # socket object
        self.server_ip = "127.0.0.1"  # server ip
        self.server_port = 8888  # connection port
        self.aes = Encryption_proj.AESEncryption()  # AES object
        self.rsa = Encryption_proj.RSACrypt()  # RSA object
        self.key = self.aes.key  # aes private key
        self.file_send_class = SendFile(self.my_socket, self.aes, self.key)  # send file object
        self.file_rcv_class = RcvFile(self.my_socket, self.aes, self.key)  # rcv file object
        self.file = None  # holds file that was received
        self.start_connection()

    def start_connection(self):
        while True:  # waits until the connection was successful
            try:
                self.my_socket.connect((self.server_ip, self.server_port))
                break
            except socket.error:
                pass
        self.rsa.public_key = pickle.loads(self.my_socket.recv(1024))
        # gets the clients private key for the AES encryption
        self.my_socket.send(self.rsa.encrypt(self.key))
        self.rcv_file()

    def rcv_file(self):
        self.file = self.file_rcv_class.rcv_file()

    def rcv(self):
        return self.aes.decrypt_aes(self.my_socket.recv(1024), self.key)

    def send(self, data):
        # sends the data and when he send exit closes the connection
        self.my_socket.send(self.aes.encrypt_aes(data, self.key))
        if data == "exit".encode():
            self.my_socket.close()

    def send_file(self, file):
        self.file_send_class.send_file(file)

    def close(self):
        self.my_socket.close()


class ServerP2P(object):
    # creates the p2p server and talks to the client on the socket
    def __init__(self, file):
        self.sock = socket.socket()  # socket object
        self.port = 8888  # holds the connection port
        self.file = file  # holds the file to send to the client
        self.client_sock = None  # clients socket
        self.rsa = Encryption_proj.RSACrypt()  # rsa object
        self.rsa.create_public_key()
        self.public_key = self.rsa.public_key  # holds rsa public key
        self.aes = Encryption_proj.AESEncryption()  # aes object
        self.key = None  # will hold the client aes key
        self.start_connection()
        self.file_send_class = SendFile(self.client_sock, self.aes, self.key)  # send file object
        self.file_rcv_class = RcvFile(self.client_sock, self.aes, self.key)  # rcv file object

    def start_connection(self):
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.listen(1)
        self.client_sock, address = self.sock.accept()
        self.client_sock.send(pickle.dumps(self.public_key))
        self.key = self.rsa.decode(self.client_sock.recv(1024))

    def rcv(self):
        return self.aes.decrypt_aes(self.client_sock.recv(1024), self.key)

    def send(self, data):
        # sends the data and when he send exit closes the connection
        self.client_sock.send(self.aes.encrypt_aes(data, self.key))
        if data == "exit".encode():
            self.sock.close()

    def send_file(self, file):
        self.file_send_class.send_file(file)

    def rcv_file(self):
        self.file = self.file_rcv_class.rcv_file()

    def close(self):
        self.sock.close()


class RcvFile(object):
    # rcv the file from the other user
    def __init__(self, sock, aes, key):
        self.sock = sock  # the socket you will rcv the file on
        self.key = key  # holds the aes key
        self.aes = aes  # holds the aes object

    def rcv_file(self):
        # gets the file file from the other person and when he sees the done sending
        # has arrived the client has the full file and removes the done sending and saves the file
        answer = pickle.loads(self.sock.recv(1024))
        answer = answer.split(" ", 1)
        answer[1] = answer[1].split("\\")[-1]
        with open(answer[1], "wb") as f:
            data = self.sock.recv(BUFFER_SIZE)
            while "done sending".encode() not in data:
                bytes_read = self.aes.decrypt_aes(data, self.key)
                f.write(bytes_read)
                data = self.sock.recv(BUFFER_SIZE)
            data = data[0:-12]
            bytes_read = self.aes.decrypt_aes(data, self.key)
            f.write(bytes_read)
        return answer[1]


class SendFile(object):
    # sends the file to the other user
    def __init__(self, sock, aes, key):
        self.sock = sock  # the socket you will send the file on
        self.aes = aes  # the aes object
        self.key = key  # the aes private key

    def send_file(self, file):
        # sends the file with done sending at the end so that the other client
        # will now when the client has sent the whole file
        with open(file, "rb") as f:
            f = f.read()
            f = self.aes.encrypt_aes(f, self.key)
            f += "done sending".encode()
        self.sock.send(pickle.dumps(str(os.path.getsize(file)) + " " + file))
        progress = tqdm.tqdm(range(os.path.getsize(file)), f"Sending {file}", unit="B", unit_scale=True,
                             unit_divisor=1024, disable=True)
        counter = 0
        for _ in progress:
            # read the bytes from the file
            bytes_read = f[BUFFER_SIZE * counter:BUFFER_SIZE * (counter + 1)]
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in
            # busy networks
            counter += 1
            self.sock.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))
