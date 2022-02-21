import socket
import threading
import config

ip = config.get_ip()


class VideoServer:
    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((ip, port))
        self.sock.listen(3)
        #self.main_server = self.sock.accept()[0]
        #threading.Thread(target=self.recv_end_signal).start()

        self.clients = []
        self.clients.append(self.sock.accept()[0])
        self.clients.append(self.sock.accept()[0])

        threading.Thread(target=lambda: self.receive_data(0)).start()
        threading.Thread(target=lambda: self.receive_data(1)).start()

    def recv_end_signal(self):
        data = ''
        while not data:
            try:
                data = self.main_server.recv(4096)
            except Exception:
                continue
        print('breaking')
        self.main_server.close()
        self.clients[0].close()
        self.clients[1].close()

    def receive_data(self, num):
        try:
            while True:
                print('forwarding')
                self.clients[1 - num].sendall(self.clients[num].recv(4096))
        except ConnectionAbortedError or OSError:
            pass
n = VideoServer(8080)