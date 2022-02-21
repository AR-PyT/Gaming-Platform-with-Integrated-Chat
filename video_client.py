import cv2
import threading
import socket
import struct
import pickle
import config

ip = '10.7.152.90'


class VidReceiver:
    def __init__(self, port):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((ip, port))

        self.vid = cv2.VideoCapture(0)

        self.payload_length = struct.calcsize("i")
        self.data = b''

        threading.Thread(target=self.receive_data).start()
        threading.Thread(target=self.capture_vid).start()

    def receive_data(self):
        try:
            while True:
                print('receiving')
                while len(self.data) < self.payload_length:
                    self.data += self.conn.recv(4096)

                msg_size = self.data[:self.payload_length]
                self.data = self.data[self.payload_length:]

                msg_len = struct.unpack('i', msg_size)

                while len(self.data) < msg_len[0]:
                    self.data += self.conn.recv(4096)

                actual_data = self.data[:msg_len[0]]
                self.data = self.data[msg_len[0]:]

                img = pickle.loads(actual_data)

                cv2.imshow('video', img)
        #except ConnectionResetError or ConnectionAbortedError:
        except Exception:
            pass

    def capture_vid(self):
        try:
            while True:
                image = self.vid.read()

                data = pickle.dumps(image)

                msg_len = struct.pack("i", len(data))
                print('sending')
                self.conn.sendall(msg_len + data)
        except ConnectionResetError or ConnectionAbortedError:
            pass

n = VidReceiver(8080)