import threading
import json
import socket
import tkinter as tk
import config

ip = config.get_ip()


class TicTacToe_client:
    def __init__(self, port, name, root):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
        self.sock.send(json.dumps(name).encode('utf-8'))
        self.width = 300
        self.height = 400
        self.btn_list = []
        self.root = tk.Toplevel(root)
        self.root.geometry(str(self.width) + 'x' + str(self.height))
        self.root.title('TicTacToe')
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.give_up)

        self.c = tk.Canvas(self.root)
        self.c.configure(height=self.height, width=self.width, bg='gray')
        self.c.pack()

    def give_up(self):
        self.sock.send(json.dumps('**||GIVEUP||**').encode('utf-8'))
        self.root.destroy()


    def draw_empty_board(self):
        # Creating a 3x3 table
        self.c.create_rectangle(0, 0, 300, 100, fill='black')
        self.c.create_text(150, 50, text='TicTacToe', font=('Jokerman', 30), fill='white', tags='text')
        for i in range(1, 4):
            self.c.create_line(0, 100 + i * 100, self.width, 100 + i * 100)
            self.c.create_line(i * 100, 100, i * 100, self.height)

    def val_btn(self, num):
        row = num // 3
        col = num % 3
        self.sock.send(json.dumps((row, col)).encode('utf-8'))

    def create_btns(self):
        btn = tk.Button(self.root, text='', height=6, width=13, bg='light gray', command=lambda: self.val_btn(0),
                        state='disabled')
        self.btn_list.append(btn)
        btn = tk.Button(self.root, text='', height=6, width=13, bg='light gray', command=lambda: self.val_btn(1),
                        state='disabled')
        self.btn_list.append(btn)
        btn = tk.Button(self.root, text='', height=6, width=13, bg='light gray', command=lambda: self.val_btn(2),
                        state='disabled')
        self.btn_list.append(btn)
        btn = tk.Button(self.root, text='', height=6, width=13, bg='light gray', command=lambda: self.val_btn(3),
                        state='disabled')
        self.btn_list.append(btn)
        btn = tk.Button(self.root, text='', height=6, width=13, bg='light gray', command=lambda: self.val_btn(4),
                        state='disabled')
        self.btn_list.append(btn)
        btn = tk.Button(self.root, text='', height=6, width=13, bg='light gray', command=lambda: self.val_btn(5),
                        state='disabled')
        self.btn_list.append(btn)
        btn = tk.Button(self.root, text='', height=6, width=13, bg='light gray', command=lambda: self.val_btn(6),
                        state='disabled')
        self.btn_list.append(btn)
        btn = tk.Button(self.root, text='', height=6, width=13, bg='light gray', command=lambda: self.val_btn(7),
                        state='disabled')
        self.btn_list.append(btn)
        btn = tk.Button(self.root, text='', height=6, width=13, bg='light gray', command=lambda: self.val_btn(8),
                        state='disabled')
        self.btn_list.append(btn)

    def drawGame(self, game_grid):
        self.c.delete('all')
        self.draw_empty_board()

        for row in range(3):
            for col in range(3):
                if game_grid[row][col] == 0:
                    self.c.create_window(col * 100 + 50, 150 + row * 100, window=self.btn_list[row * 3 + col])
                elif game_grid[row][col] == 1:
                    self.c.create_oval(col * 100 + 20, 120 + row * 100, 80 + col * 100, 180 + row * 100, width=2)
                elif game_grid[row][col] == 2:
                    self.c.create_line(col * 100, 200 + row * 100, 100 + col * 100, 100 + row * 100, width=2,
                                       fill='black')
                    self.c.create_line(col * 100, 100 + row * 100, 100 + col * 100, 200 + row * 100, width=2,
                                       fill='black')

    def draw_win_line(self, key):
        if key[-3:] == '--0':
            self.c.delete('text')
            self.c.create_text(150, 50, text='DRAW', font=('chiller', 40), fill='white')
            return
        key = key[4:]
        if key[0] == 'R':
            self.c.create_line(0, 150 + int(key[1]) * 100, self.width, 150 + int(key[1]) * 100, fill='red', width=4)
        elif key[0] == 'C':
            self.c.create_line(50 + int(key[1]) * 100, 100, 50 + int(key[1]) * 100, 400, fill='red', width=4)
        elif key[0:2] == 'DL':
            self.c.create_line(0, 100, 300, 400, fill='red', width=4)
        elif key[0:2] == 'DR':
            self.c.create_line(0, 400, 300, 100, fill='red', width=4)
        self.c.delete('text')
        string = key[2:] + ' Wins'
        self.c.create_text(150, 50, text=string, font=('chiller', 30), fill='white')

    def shut_down(self):
        self.root.destroy()

    def play_game(self):
        while True:
            received = False
            while not received:
                try:
                    game_board = json.loads(self.sock.recv(4096).decode('utf-8'))
                    received = True
                except json.decoder.JSONDecodeError:
                    pass
            print(game_board)
            if game_board == 'move':
                self.c.delete('wait')
                self.c.create_text(300, 100, text='YOUR TURN', anchor='se', font=('Times New Roman', 12), fill='cyan', tag='move')
                for i in range(9):
                    self.btn_list[i].configure(state='normal')
            elif game_board[:4] == 'OVER':
                self.c.delete('move')
                self.c.delete('wait')
                self.root.protocol("WM_DELETE_WINDOW", self.shut_down)
                self.draw_win_line(game_board)
                break
            else:
                for i in range(9):
                    self.btn_list[i].configure(state='disabled')
                self.c.delete('move')
                self.c.create_text(300, 100, text='WAIT', anchor='se', font=('Times New Roman', 12), fill='red', tag='wait')
                self.drawGame(game_board)

    def run(self):
        self.draw_empty_board()
        self.create_btns()
        self.drawGame([[0, 0, 0], [0, 0, 0], [0, 0, 0]])

        play = threading.Thread(target=self.play_game)
        play.start()

        # self.root.mainloop()
