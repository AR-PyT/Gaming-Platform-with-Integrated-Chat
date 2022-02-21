import json
import socket
import tictac_engine
import threading
import time
import config
import sqlite3 as db

ip = config.get_ip()


class TicTacServer:
    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((ip, port))
        self.sock.listen(5)

        self.turn = 0

        p1 = self.sock.accept()
        p2 = self.sock.accept()

        self.game = tictac_engine.TicTacToe()
        self.p1name = ''
        self.p2name = ''

        self.players = [p1, p2]
        self.do_send = True

        threading.Thread(target=self.get_name_1).start()
        threading.Thread(target=self.get_name_2).start()

        while not (self.p1name and self.p2name):
            pass

    def get_name_1(self):
        data = ''
        while not data:
            try:
                data = json.loads(self.players[0][0].recv(4096).decode('utf-8'))
            except json.JSONDecodeError:
                continue
        self.p1name = data

    def get_name_2(self):
        data = ''
        while not data:
            try:
                data = json.loads(self.players[1][0].recv(4096).decode('utf-8'))
            except json.JSONDecodeError:
                continue
        self.p2name = data

    def receive_data(self, player_num):
        received = False
        while not received:
            try:
                data = json.loads(self.players[player_num][0].recv(4096).decode('utf-8'))
                received = True
            except ConnectionResetError:
                pass
        return data

    def send_grid(self):
        game_grid = json.dumps(self.game.game_grid.copy().tolist())
        for player in self.players:
            player[0].send(game_grid.encode('utf-8'))
        time.sleep(1)

    def update_db(self, winner):
        connection = db.connect('details.db')
        cursor = connection.cursor()

        if winner == 0:
            records = cursor.execute(
                f"SELECT user_name, tt_draw FROM accounts WHERE user_name = '{self.p1name}' OR user_name = '{self.p2name}';")
            for record in records:
                new_draw = record[1] + 1
                cursor.execute(f"UPDATE accounts SET tt_draw = {new_draw} WHERE user_name = '{record[0]}'")
        elif winner == 1:
            record = cursor.execute(f"SELECT tt_win FROM accounts WHERE user_name = '{self.p1name}'")
            for data in record:
                new_win = data[0] + 1
            cursor.execute(f"UPDATE accounts SET tt_win = {new_win} WHERE user_name = '{self.p1name}'")

            record = cursor.execute(f"SELECT tt_loss FROM accounts WHERE user_name = '{self.p2name}'")
            for data in record:
                new_loss = data[0] + 1
            cursor.execute(f"UPDATE accounts SET tt_loss = {new_loss} WHERE user_name = '{self.p2name}'")
        elif winner == 2:
            record = cursor.execute(f"SELECT tt_win FROM accounts WHERE user_name = '{self.p2name}'")
            for data in record:
                new_win = data[0] + 1
            cursor.execute(f"UPDATE accounts SET tt_win = {new_win} WHERE user_name = '{self.p2name}'")

            record = cursor.execute(f"SELECT tt_loss FROM accounts WHERE user_name = '{self.p1name}'")
            for data in record:
                new_loss = data[0] + 1
            cursor.execute(f"UPDATE accounts SET tt_loss = {new_loss} WHERE user_name = '{self.p1name}'")

        connection.commit()
        connection.close()

    def send_move(self):
        while self.do_send:
            self.send_grid()
            self.players[self.turn][0].send(json.dumps('move').encode('utf-8'))
            time.sleep(10)

    def run(self):
        self.send_grid()
        threading.Thread(target=lambda: self.send_move).start()
        for i in range(5):
            self.turn = 0
            self.players[self.turn][0].send(json.dumps('move').encode('utf-8'))
            move_data = self.receive_data(0)

            if move_data == '**||GIVEUP||**':
                self.players[1 - self.turn][0].send(json.dumps('OVER--' + self.p1name).encode('utf-8'))
                self.do_send = False
                for player in self.players:
                    player[0].close()
                break

            self.game.add_player_1(move_data)
            self.send_grid()
            val = self.game.check_winner(1)
            if val:
                for player in self.players:
                    player[0].send(json.dumps('OVER' + val + self.p1name).encode('utf-8'))
                self.update_db(1)
                break
            if i == 4:
                for player in self.players:
                    player[0].send(json.dumps('OVER' + '--0').encode('utf-8'))
                self.update_db(0)
                break
            self.turn = 1
            self.players[self.turn][0].send(json.dumps('move').encode('utf-8'))

            move_data = self.receive_data(1)

            if move_data == '**||GIVEUP||**':
                self.players[1 - self.turn][0].send(json.dumps('OVER--' + self.p2name).encode('utf-8'))
                self.do_send = False
                self.update_db(2 - self.turn)
                for player in self.players:
                    player[0].close()
            self.game.add_player_2(move_data)
            self.send_grid()
            val = self.game.check_winner(2)
            if val:
                for player in self.players:
                    player[0].send(json.dumps('OVER' + val + self.p2name).encode('utf-8'))
                self.update_db(2)
                break
