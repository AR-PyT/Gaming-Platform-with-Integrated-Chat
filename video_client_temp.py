import cv2
import pyaudio
import threading
import socket
import pickle
import time
import json
import config

ip = config.get_ip()


class VidClient:
    def __init__(self, port):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((ip, port))

        self.vid_capture = cv2.VideoCapture(0)
        sound_object = pyaudio.PyAudio()
        self.input_stream = sound_object.open(format=pyaudio.paInt24, channels=2, rate=44100, frames_per_buffer=1024,
                                              input=True)
        self.output_stream = sound_object.open(format=pyaudio.paInt24, channels=2, rate=44100, frames_per_buffer=1024,
                                               output=True)

        self.recorded_sound = []

        # Whether u r sending data or not deals with ok problem i.e. ok appended into sent image sound data
        self.sending = False

        #threading.Thread(target=self.capture_sound).start()
        #threading.Thread(target=self.capture_video).start()
        threading.Thread(target=self.receive_data).start()

    def capture_sound(self):
        while True:
            self.recorded_sound.append(self.input_stream.read(1024))

    def capture_video(self):
        while True:
            image = self.vid_capture.read(0)[1]
            if len(self.recorded_sound) > 10:
                print('sending')
                self.sending = True

                data = pickle.dumps([self.recorded_sound.copy(), image])
                self.conn.send(json.dumps(len(data)).encode('utf-8'))
                if self.conn.recv(4096) == b'"ok"': print('yes')
                #time.sleep(0.25)
                self.conn.send(data)
                self.recorded_sound = []
                self.sending = False

    def play_sound(self, sounds):
        for sound in sounds:
            self.output_stream.write(sound)

    def receive_data(self):
        while True:
            # image = self.vid_capture.read(0)[1]
            # if len(self.recorded_sound) > 10:
            #     print('sending')
            #     send_data = pickle.dumps([self.recorded_sound.copy(), image])
            #     self.conn.send(json.dumps(len(send_data)).encode('utf-8'))
            #     if self.conn.recv(4096) == b'"ok"': print('yes')
            #
            #     self.conn.send(send_data)
            #     self.recorded_sound = []

            try:
                message_length = json.loads(self.conn.recv(4096).decode('utf-8'))
                self.conn.send(json.dumps('ok').encode('utf-8'))
                #time.sleep(0.25)
                received_length = 0
                fragments = []

                while received_length < message_length:

                    chunk = self.conn.recv(message_length - received_length)
                    if not chunk:
                        break
                    fragments.append(chunk)
                    received_length += len(chunk)

                data = pickle.loads(b"".join(fragments))
            except Exception as e:
                print(e)
                print('ignored')
                continue
            threading.Thread(target=lambda: self.play_sound(data[0])).start()
            cv2.imshow('video', data[1])



            if cv2.waitKey(1) & 0xFF == ord('q'):
                continue

