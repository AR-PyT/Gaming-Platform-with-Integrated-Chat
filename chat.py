import tkinter as tk
import json
from tkinter import messagebox
import socket
import threading
import tictactoe_client
import audio_client
import chess_client
import config

ip = config.get_ip()


class Chat:
    def __init__(self, port, your_name, other_name, top):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((ip, int(port)))
        self.conn.send(json.dumps(your_name).encode('utf-8'))
        self.your_name = your_name
        self.other_name = other_name
        self.root = tk.Toplevel(top)
        self.root.geometry('400x400')
        self.root.title(self.other_name)
        self.root.resizable(False, False)

        self.img3 = tk.PhotoImage(file='.\\images\\game_choose.png')
        self.img2 = tk.PhotoImage(file='.\\images\\Chat.png')
        self.vid = tk.PhotoImage(file='.\\images\\video.png')
        self.game = tk.PhotoImage(file='.\\images\\game.png')
        self.back = tk.PhotoImage(file='.\\images\\return4.png')
        self.send = tk.PhotoImage(file='.\\images\\send.png')

        self.in_selection = False

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.c = tk.Canvas(self.root, height=400, width=400, bg='black')
        self.c.pack()

        self.entry = tk.Entry(self.root, width=60)
        self.chat = []

        threading.Thread(target=self.receive_data).start()

    def on_close(self):
        self.conn.send(json.dumps('**||CLOSE||**').encode('utf-8'))
        self.root.destroy()

    def shut_down(self):
        self.root.destroy()

    def start_video_receiving(self, port):
        # try:
        #     audio_receiver.AudioReceiver(int(port))
        # except Exception as e:
        #     print(e)
        #     pass
        audio_client.AudioReceiver(int(port))

    def start_video_sending(self, port):
        #try:
        #     audio_sender.AudioSender(int(port))
        # except Exception as e:
        #     print(e)
        #     pass
        #audio_sender.AudioSender(int(port))
        audio_client.AudioReceiver(int(port))

    def receive_data(self):
        while True:
            try:
                data = json.loads(self.conn.recv(4096).decode('utf-8'))
            except json.JSONDecodeError:
                continue
            if data == '**|T|PORT|T|**':
                ans = messagebox.askquestion(title='Game Request', message='Start a TicTacToe Match?')
                if ans == 'yes':
                    self.conn.send(json.dumps('**||PORT||**').encode('utf-8'))
                else:
                    self.conn.send(json.dumps('**||||**').encode('utf-8'))
            elif data == '**|C|PORT|C|**':
                ans = messagebox.askquestion(title='Game Request', message='Start a Chess Match?')
                if ans == 'yes':
                    self.conn.send(json.dumps('**C||PORT||C**').encode('utf-8'))
                else:
                    self.conn.send(json.dumps('**||||**').encode('utf-8'))
            elif data == '**|VID||VID|**':
                ans = messagebox.askquestion(title='Audio Request', message='Start an Audio Chat?')
                if ans == 'yes':
                    self.conn.send(json.dumps('**VID||PORT||VID**').encode('utf-8'))
                else:
                    self.conn.send(json.dumps('**||||**').encode('utf-8'))
            elif '^R^VID||VID^R^ ' in data:
                print('starting11')
                threading.Thread(target=lambda: self.start_video_receiving(data.split(' ')[1])).start()
            elif '^S^VID||VID^S^ ' in data:
                print('starting22')
                threading.Thread(target=lambda: self.start_video_sending(data.split(' ')[1])).start()
            elif data == '**||||**':
                messagebox.showwarning(title='Rejected', message='Request was rejected')
            elif data[0:9] == '^^T||T^^ ':
                threading.Thread(target=lambda: self.play_tictac(data.split(' ')[1])).start()
            elif data[0:9] == '^^C||C^^ ':
                threading.Thread(target=lambda: self.play_chess(data.split(' ')[1])).start()
            elif data == '**||CLOSE||**':
                self.entry.delete(0, tk.END)
                self.entry.configure(state='disabled')
                self.entry.unbind('<Return>')

                self.chat.append(('l', ' '))
                self.chat.append(('l', ' '))

                self.update()
                txt = self.other_name + ' has left the room'
                self.c.create_text(200, 350, anchor=tk.S, text=txt, font=('Jokerman', 20), fill='purple')
                self.root.protocol("WM_DELETE_WINDOW", self.shut_down)
                break
            else:
                self.chat.append(('l', data))
                self.update()

    def send_data(self):
        data = self.entry.get()
        if data == '': return
        self.chat.append(('r', data))
        self.update()
        self.conn.send(json.dumps(data).encode('utf-8'))
        self.entry.delete(0, tk.END)

    def play_tictac(self, port):
        new = tictactoe_client.TicTacToe_client(int(port), self.your_name, self.root)
        new.run()

    def play_chess(self, port):
        new = chess_client.ChessClient(int(port), self.your_name)
        new.game_play()

    def click(self, event):
        x, y = event.x, event.y
        if 55 < int(x) < 170 and 110 < int(y) < 220:
            self.conn.send(json.dumps('**|T|PORT|T|**').encode('utf-8'))
        elif 230 < int(x) < 340 and 110 < int(y) < 220:
            self.conn.send(json.dumps('**|C|PORT|C|**').encode('utf-8'))
        elif 150 < int(x) < 255 and 270 < int(y) < 370:
            print('shoot')
        elif 30 < int(x) < 90 and 15 < int(y) < 45:
            self.c.delete('selection')
            self.in_selection = False
            self.display()
            self.update()

    def choose_game(self):
        self.c.delete('chat')
        self.c.delete('norm')
        self.c.delete('aud')

        self.c.bind('<ButtonRelease-1>', self.click)

        self.c.create_image(0, 0, anchor='nw', image=self.img3, tag='selection')
        self.c.create_image(30, 15, anchor='nw', image=self.back, tag='selection')

        self.in_selection = True

    def close_video(self):
        self.conn.send(json.dumps('**||AUDIO CLOSE||**').encode('utf-8'))
        self.c.delete('cl_aud')
        self.display()

    def start_video(self):
        self.c.delete('aud')

        play_btn = tk.Button(self.root, height=45, width=70, image=self.vid, command=self.close_video)
        self.c.create_window(30, 3, window=play_btn, anchor='nw', tag='cl_aud')

        self.conn.send(json.dumps('**|VID||VID|**').encode('utf-8'))

    def display(self):
        self.c.create_image(0, 50, image=self.img2, anchor='nw', tag='norm')
        self.c.create_rectangle(0, 0, 400, 55, fill='gray', tag='norm')

        play_btn = tk.Button(self.root, height=45, width=70, image=self.vid, command=self.start_video)
        self.c.create_window(30, 3, window=play_btn, anchor='nw', tag='aud')

        play_btn2 = tk.Button(self.root, height=45, width=70, image=self.game, command=self.choose_game)
        self.c.create_window(300, 3, window=play_btn2, anchor='nw', tag='aud')

        self.c.create_window(182, 388, window=self.entry, tag='norm')
        send_btn = tk.Button(self.root, height=15, width=25, image=self.send, command=self.send_data)
        self.c.create_window(365, 378, anchor='nw', window=send_btn, tag='norm')

    def update(self):
        if self.in_selection:
            return
        self.c.delete('chat')
        space = 15
        for msg in self.chat[::-1]:
            if space < 3: return
            for i in range(len(msg[1]), -1, -35):
                if i - 35 < 0: i = 35
                if msg[0] == 'r':
                    self.c.create_text(390, 23 * space, text=msg[1][i - 35:i + 1], fill='black', anchor=tk.SE,
                                       tag='chat')
                elif msg[0] == 'l':
                    self.c.create_text(10, 23 * space, text=msg[1][i - 35:i + 1], fill='red', anchor=tk.SW, tag='chat')
                space -= 1

    def entered(self, event):
        self.send_data()

    def run(self):
        self.display()
        self.entry.bind('<Return>', self.entered)
