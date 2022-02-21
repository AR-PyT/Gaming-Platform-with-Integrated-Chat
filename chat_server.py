import socket
import json
import threading
import tictactoe_server
import chess_server
import audio_server
import config
import time

ip = config.get_ip()


class ChatServerIndividual:
    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_audio = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((ip, port))
        self.sock.listen(5)
        self.client1 = self.sock.accept()[0]
        self.client2 = self.sock.accept()[0]
        self.client1_name = ''
        self.client2_name = ''

        threading.Thread(target=self.get_name_1).start()
        threading.Thread(target=self.get_name_2).start()

        while not (self.client1_name and self.client2_name):
            pass

        self.avail_port = 9000
        self.chat_ongoing = True

        threading.Thread(target=self.receive_messages_client1).start()
        threading.Thread(target=self.receive_messages_client2).start()

    def get_name_1(self):
        data = ''
        while not data:
            try:
                data = json.loads(self.client1.recv(4096).decode('utf-8'))
            except json.JSONDecodeError:
                continue
        self.client1_name = data

    def get_name_2(self):
        data = ''
        while not data:
            try:
                data = json.loads(self.client2.recv(4096).decode('utf-8'))
            except json.JSONDecodeError:
                continue
        self.client2_name = data

    def tictac_server(self):
        new = tictactoe_server.TicTacServer(self.avail_port)
        new.run()

    def chess_server(self):
        new = chess_server.ChessServer(self.avail_port)
        new.run_game()

    def vid_server(self):
        try:
            new = audio_server.AudioServer(self.avail_port)
        except Exception as e:
            print(e)
            pass

    def receive_messages_client1(self):
        while self.chat_ongoing:
            try:
                data = json.loads(self.client1.recv(4096).decode('utf-8'))
            except json.JSONDecodeError or ConnectionAbortedError or ConnectionResetError:
                continue
            if data == '**||PORT||**':
                threading.Thread(target=self.tictac_server).start()
                self.client1.send(json.dumps('^^T||T^^ ' + str(self.avail_port)).encode('utf-8'))
                self.client2.send(json.dumps('^^T||T^^ ' + str(self.avail_port)).encode('utf-8'))
                self.avail_port += 1
            elif data == '**C||PORT||C**':
                threading.Thread(target=self.chess_server).start()
                self.client1.send(json.dumps('^^C||C^^ ' + str(self.avail_port)).encode('utf-8'))
                self.client2.send(json.dumps('^^C||C^^ ' + str(self.avail_port)).encode('utf-8'))
                self.avail_port += 1
            elif data == '**VID||PORT||VID**':
                print('STARITING')
                threading.Thread(target=self.vid_server).start()
                self.sock_audio.connect((ip, self.avail_port))
                self.client1.send(json.dumps('^R^VID||VID^R^ ' + str(self.avail_port)).encode('utf-8'))
                self.client2.send(json.dumps('^S^VID||VID^S^ ' + str(self.avail_port)).encode('utf-8'))
                self.avail_port += 1
                print('started')
                # time.sleep(2)
                # threading.Thread(target=self.vid_server).start()
                # self.client2.send(json.dumps('^R^VID||VID^R^ ' + str(self.avail_port)).encode('utf-8'))
                # self.client1.send(json.dumps('^S^VID||VID^S^ ' + str(self.avail_port)).encode('utf-8'))
                # self.avail_port += 1
            elif data == '**||CLOSE||**':
                self.client2.send(json.dumps('**||CLOSE||**').encode('utf-8'))
                self.chat_ongoing = False
                self.client1.close()
                self.client2.close()
                break
            elif data == '**||AUDIO CLOSE||**':
                self.sock_audio.send(json.dumps('close').encode('utf-8'))
            else:
                self.client2.send(json.dumps(data).encode('utf-8'))

    def receive_messages_client2(self):
        while self.chat_ongoing:
            try:
                data = json.loads(self.client2.recv(4096).decode('utf-8'))
            except json.JSONDecodeError or ConnectionAbortedError or ConnectionResetError:
                continue
            if data == '**||PORT||**':
                threading.Thread(target=self.tictac_server).start()
                self.client1.send(json.dumps('^^T||T^^ ' + str(self.avail_port)).encode('utf-8'))
                self.client2.send(json.dumps('^^T||T^^ ' + str(self.avail_port)).encode('utf-8'))
                self.avail_port += 1
            elif data == '**C||PORT||C**':
                threading.Thread(target=self.chess_server).start()
                self.client1.send(json.dumps('^^C||C^^ ' + str(self.avail_port)).encode('utf-8'))
                self.client2.send(json.dumps('^^C||C^^ ' + str(self.avail_port)).encode('utf-8'))
                self.avail_port += 1
            elif data == '**VID||PORT||VID**':
                print('STARTING VID')
                threading.Thread(target=self.vid_server).start()
                self.sock_audio.connect((ip, self.avail_port))
                self.client1.send(json.dumps('^R^VID||VID^R^ ' + str(self.avail_port)).encode('utf-8'))
                self.client2.send(json.dumps('^S^VID||VID^S^ ' + str(self.avail_port)).encode('utf-8'))
                print('started')
                self.avail_port += 1
                # time.sleep(2)
                # threading.Thread(target=self.vid_server).start()
                # self.client2.send(json.dumps('^R^VID||VID^R^ ' + str(self.avail_port)).encode('utf-8'))
                # self.client1.send(json.dumps('^S^VID||VID^S^ ' + str(self.avail_port)).encode('utf-8'))
                # self.avail_port += 1
            elif data == '**||CLOSE||**':
                self.client1.send(json.dumps('**||CLOSE||**').encode('utf-8'))
                self.chat_ongoing = False
                self.client1.close()
                self.client2.close()
                break
            elif data == '**||AUDIO CLOSE||**':
                self.sock_audio.send(json.dumps('close').encode('utf-8'))
                self.sock_audio.close()
                self.sock_audio = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            else:
                self.client1.send(json.dumps(data).encode('utf-8'))
