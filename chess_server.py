import chess_engine
import json
import socket
import sqlite3 as db
import threading
import time
import config

ip = config.get_ip()


# 0 is P1 and 1 is P2 with w, b
class ChessServer:
    def __init__(self, port):
        self.engine = chess_engine.ChessEngine()
        self.colors = {0: 'w', 1: 'b'}
        self.moves = [[0] * 8] * 8
        self.turn = 0

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((ip, port))
        sock.listen(5)
        self.conn = [None, None]
        self.name1 = ''
        self.name2 = ''
        self.conn[0] = sock.accept()[0]
        self.conn[1] = sock.accept()[0]
        self.game_ongoing = True

        threading.Thread(target=self.get_name1).start()
        threading.Thread(target=self.get_name2).start()

        while not (self.name1 and self.name2):
            pass

        self.names = [self.name1, self.name2]

    def get_name1(self):
        data = ''
        while not data:
            try:
                data = json.loads(self.conn[0].recv(4096).decode('utf-8'))
            except json.JSONDecodeError:
                pass
        self.name1 = data

    def get_name2(self):
        data = ''
        while not data:
            try:
                data = json.loads(self.conn[1].recv(4096).decode('utf-8'))
            except json.JSONDecodeError:
                pass
        self.name2 = data

    def update_database(self):
        connection = db.connect('details.db')
        cursor = connection.cursor()

        records = list(cursor.execute(
            f"SELECT user_name, ch_win, ch_loss FROM accounts WHERE user_name = '{self.names[self.turn]}' OR user_name = '{self.names[1 - self.turn]}';"))
        for record in records:
            print('updating database for ', record[0])
            if record[0] == self.names[self.turn]:
                new_win = record[1] + 1
                cursor.execute(f"UPDATE accounts SET ch_win = {new_win} WHERE user_name = '{record[0]}'")
            else:
                new_loss = record[2] + 1
                cursor.execute(f"UPDATE accounts SET ch_loss = {new_loss} WHERE user_name = '{record[0]}'")
        connection.commit()
        connection.close()

    def get_data(self):
        try:
            point = json.loads(self.conn[self.turn].recv(4096).decode('utf-8'))
        except json.JSONDecodeError:
            return

        if point == '**||GIVEUP||**':
            self.conn[1 - self.turn].send(json.dumps('OVER ' + self.names[1 - self.turn]).encode('utf-8'))
            self.turn = 1 - self.turn
            self.game_ongoing = False

            self.update_database()
            self.conn[0].close()
            self.conn[1].close()

            return


        if self.moves[point[1]][point[0]] != 0:
            if self.engine.board[self.engine.recent_piece[1]][self.engine.recent_piece[1]][1] == 'p' and (
                    point[1] == 7 or point[1] == 0):
                self.conn[self.turn].send(json.dumps('promote' + self.colors[self.turn]).encode('utf-8'))
                self.engine.board[self.engine.recent_piece[1]][self.engine.recent_piece[0]] = json.loads(
                    self.conn[self.turn].recv(4096).decode('utf-8'))
            self.moves = [[0] * 8] * 8
            self.engine.move_piece(point)
            if self.engine.checkWinner(self.colors[1 - self.turn]):
                self.send_board()

                self.conn[self.turn].send(json.dumps('OVER ' + self.names[self.turn]).encode('utf-8'))
                self.conn[1 - self.turn].send(json.dumps('OVER ' + self.names[self.turn]).encode('utf-8'))

                self.conn[0].close()
                self.conn[1].close()

                self.update_database()

                self.turn = 1 - self.turn

                return 'over'

            self.turn = 1 - self.turn
            return
        return point

    def send_board(self):
        self.conn[1 - self.turn].send(json.dumps(self.engine.board.tolist()).encode('utf-8'))
        time.sleep(0.5)
        self.conn[self.turn].send(json.dumps(self.engine.board.tolist()).encode('utf-8'))

    def run_game(self):
        self.send_board()
        while self.game_ongoing:
            self.conn[self.turn].send(json.dumps('turn').encode('utf-8'))
            self.conn[1 - self.turn].send(json.dumps('wait').encode('utf-8'))
            pos = self.get_data()
            if pos == 'over':
                break
            elif pos:
                self.moves = self.engine.possible_moves(pos, self.colors[self.turn])

            if self.moves:
                self.moves.append(0)
                self.conn[self.turn].send(json.dumps(self.moves).encode('utf-8'))
            self.send_board()
