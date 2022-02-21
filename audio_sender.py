import pyaudio
import socket
import pickle
import struct
import config

ip = config.get_ip()


class AudioSender:
    def __init__(self, port):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((ip, port))

        sound_object = pyaudio.PyAudio()
        self.input_stream = sound_object.open(format=pyaudio.paInt24, channels=2, rate=44100, frames_per_buffer=1024,
                                              input=True)

        self.recorded_sound = []
        self.capture_sound()

    def capture_sound(self):
        try:
            while True:
                self.recorded_sound.append(self.input_stream.read(1024))
                if len(self.recorded_sound) > 5:
                    data = pickle.dumps(self.recorded_sound.copy())
                    self.recorded_sound = []

                    msg_len = struct.pack("i", len(data))
                    print('sending')

                    self.conn.sendall(msg_len + data)
        except ConnectionResetError or ConnectionAbortedError:
            pass