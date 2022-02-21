import pyaudio
import threading
import socket
import struct
import pickle
import config

ip = config.get_ip()


class AudioReceiver:
    def __init__(self, port):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((ip, port))

        sound_object = pyaudio.PyAudio()
        self.output_stream = sound_object.open(format=pyaudio.paInt24, channels=2, rate=44100, frames_per_buffer=1024,
                                               output=True)

        self.input_stream = sound_object.open(format=pyaudio.paInt24, channels=2, rate=44100, frames_per_buffer=1024,
                                              input=True)

        self.recorded_sound = []
        self.payload_length = struct.calcsize("i")
        self.data = b''

        threading.Thread(target=self.receive_data).start()
        threading.Thread(target=self.capture_sound).start()

    def play_sound(self, sounds):
        for sound in sounds:
            self.output_stream.write(sound)

    def receive_data(self):
        try:
            while True:
                print('receiving')
                while len(self.data) < self.payload_length:
                    print('stuck1')
                    self.data += self.conn.recv(4096)

                msg_size = self.data[:self.payload_length]
                self.data = self.data[self.payload_length:]

                msg_len = struct.unpack('i', msg_size)
                print(msg_len)

                while len(self.data) < msg_len[0]:
                    print('stuck2')
                    self.data += self.conn.recv(4096)

                actual_data = self.data[:msg_len[0]]
                self.data = self.data[msg_len[0]:]

                sound = pickle.loads(actual_data)
                threading.Thread(target=lambda: self.play_sound(sound)).start()

        except ConnectionResetError or ConnectionAbortedError:
            pass

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
