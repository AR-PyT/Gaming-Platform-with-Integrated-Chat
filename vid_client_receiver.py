import cv2
import pyaudio
import threading
import socket
import struct
import pickle
import json
import config

ip = config.get_ip()


class VidClient:
    def __init__(self, port):
        print(port)
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('conn')
        self.conn.connect((ip, port))
        print('(made')

        self.vid_capture = cv2.VideoCapture(0)
        self.wait_time = 0
        sound_object = pyaudio.PyAudio()
        self.output_stream = sound_object.open(format=pyaudio.paInt24, channels=2, rate=44100, frames_per_buffer=1024,
                                               output=True)

        # Whether u r sending data or not deals with ok problem i.e. ok appended into sent image sound data

        self.payload_length = struct.calcsize("i")
        self.data = b''

        threading.Thread(target=self.receive_data).start()
        print('Started')

    def play_sound(self, sounds):
        for sound in sounds:
            self.output_stream.write(sound)

    def receive_data(self):
        while True:
            print('receiving')

            while len(self.data) < self.payload_length:
                self.data += self.conn.recv(4096)

            msg_size = self.data[:self.payload_length]
            self.data = self.data[self.payload_length:]

            msg_len = struct.unpack('i', msg_size)
            print(type(msg_size))

            while len(self.data) < msg_len[0]:
                self.data += self.conn.recv(4096)

            actual = self.data[:msg_len[0]]
            self.data = self.data[msg_len[0]:]

            img = pickle.loads(actual)
            # cv2.imshow('fraame', img)
            self.play_sound(img)

            # sound, img = pickle.loads(actual)
            # threading.Thread(target=lambda: self.play_sound(sound))
            # cv2.imshow('test', img)
            cv2.waitKey(1)
