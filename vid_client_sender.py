import cv2
import pyaudio
import threading
import socket
import pickle
import json
import struct
import config

ip = config.get_ip()


class VidClient:
    def __init__(self, port):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('CONNECTING')
        self.conn.connect((ip, port))

        self.vid_capture = cv2.VideoCapture(0)
        sound_object = pyaudio.PyAudio()
        self.input_stream = sound_object.open(format=pyaudio.paInt24, channels=2, rate=44100, frames_per_buffer=1024,
                                              input=True)

        self.recorded_sound = []

        # Whether u r sending data or not deals with ok problem i.e. ok appended into sent image sound data

        # self.conn.recv(4096)
        threading.Thread(target=self.capture_sound).start()
        #threading.Thread(target=self.capture_video).start()
        print('started')

    def capture_sound(self):
        while True:
            self.recorded_sound.append(self.input_stream.read(1024))
            if len(self.recorded_sound) > 5:
                data = pickle.dumps(self.recorded_sound.copy())
                # self.recorded_sound = []
                self.recorded_sound = []

                msg_len = struct.pack("i", len(data))
                print('sending')
                self.conn.sendall(msg_len + data)


    def capture_video(self):
        while True:
            ret, img = self.vid_capture.read()
            #data = pickle.dumps([self.recorded_sound.copy(), img])
            if not ret: continue
            data = pickle.dumps(img)
            #self.recorded_sound = []

            msg_len = struct.pack("i", len(data))
            print('sending')
            self.conn.sendall(msg_len + data)
