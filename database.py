import threading
import pickle
import _sqlite3
import hashlib

MAX_READER = 10


class Dict(object):
    def __init__(self, file):
        self.file = file
        self.conn = _sqlite3.connect("data.db", check_same_thread=False)
        self.cur = self.conn.cursor()
        self.dict = None
        # while True:
        #    try:

    #         with open(self.file, "rb") as file:
    #              self.dict = {}
    #               file = pickle.load(file)
    #                self.dict = file
    #                 break
    #          except EOFError:
    #               break

    def insert(self, key, value):
        self.cur.execute("INSERT INTO users VALUES (?,?,?)", (key, hashlib.sha256(value.encode()).hexdigest(), "a"))
        self.conn.commit()
        # self.dict
        # self.dict[key] = value
        # self.dict
        # with open(self.file, "wb") as file:
        #   pickle.dump(self.dict, file)

    def remove_key(self, key):
        if self.check_key(key):
            del self.dict[key]
        else:
            print("no such key")

    def get_value(self, key, value):
        self.cur.execute("SELECT * from users WHERE username = (?) AND password = (?) ",
                         (key, hashlib.sha256(value.encode()).hexdigest()))
        return True if self.cur.fetchall() else False

    def check_key(self, key):
        self.cur.execute("SELECT * from users WHERE username = (?) ", (key,))
        return True if self.cur.fetchall() else False
        # return key in self.dict


class SyncDataBase(threading.Thread):
    def __init__(self, file):
        self.dict = Dict(file)
        self.file = file
        self.answer = None
        self.lock = threading.Lock()
        self.semaphore = threading.Semaphore(MAX_READER)

    def write(self, key, value):  # method to write to dict
        self.lock.acquire()  # lock so no thread can write as another thread is writing
        for i in range(MAX_READER):
            self.semaphore.acquire()  # take all the semaphores so no one can read while thread is writing
        self.dict.insert(key, value)  # write
        for i in range(MAX_READER):  # release all threads so threads can write
            self.semaphore.release()
        self.lock.release()  # release so other threads could write

    def check(self, key):
        self.lock.acquire()  # let no thread write as thread is reading
        self.semaphore.acquire()  # take one semaphore to read
        self.lock.release()  # reduce semaphore by one
        self.answer = self.dict.check_key(key)
        self.semaphore.release()

    def check_login(self, key, value):
        self.lock.acquire()  # let no thread write as thread is reading
        self.semaphore.acquire()  # take one semaphore to read
        self.lock.release()  # reduce semaphore by one
        self.answer = self.dict.get_value(key, value)
        self.semaphore.release()
