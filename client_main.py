import tkinter as tk
import string
import socket
import json
import personalized_client
import config

ip = config.get_ip()

new_user = False

root = tk.Tk()
root.geometry('600x500')
root.title('MyGamingAPP')
root.resizable(False, False)

c = tk.Canvas(root)
c.configure(height=600, width=600, bg='black')
c.pack()

c.create_text(300, 50, text='WELCOME', font=('Times New Roman', 40), fill='white')
c.create_text(300, 100, text='TO MyGamingAPP', font=('Times New Roman', 30), fill='white')


def get_input():
    username = text_1.get()
    password = text_2.get()
    if not username or not password:
        c.create_text(300, 170, text='Enter both Username and Password', fill='red', tag='new_btn')
        return
    for element in username:
        if element not in string.ascii_letters and element != '_':
            c.create_text(300, 250, text='Only English Letters and _ allowed', fill='white', tag='new_btn')
            return
    text_2.delete(0, tk.END)
    if new_user:
        username = ' **' + username
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, 8080))
    sock.send(json.dumps([username, password]).encode('utf-8'))
    data = json.loads(sock.recv(4096).decode('utf-8'))
    if data == 'ok':
        root.destroy()
        if username[:3] == ' **': username = username[3:]

        personalized = personalized_client.PersonalWindow(sock, username)
        personalized.window.focus_get()
        personalized.run()


    elif data == 'taken':
        c.create_text(300, 335, text='Username Taken Enter New', fill='white')
    else:
        c.create_text(300, 335, text='Wrong credentials entered', fill='white', tag='new_btn')


def new_entry():
    global new_user
    new_user = True
    c.delete('new_btn')
    c.create_text(300, 150, text='ENTER USERNAME AND CREATE A STRONG PASSWORD', font=('Chiller', 20), fill='white')


text_1 = tk.Entry(root, width=50, justify='center')
text_2 = tk.Entry(root, width=50, justify='center', show='*')

btn1 = tk.Button(root, text='Submit', bg='white', relief='sunken', width=10, activebackground='gray',
                 command=lambda: get_input())
btn2 = tk.Button(root, text='Register', bg='white', relief='sunken', width=10, activebackground='gray',
                 command=lambda: new_entry())

c.create_text(300, 200, text='USERNAME', font=('Verdana', 20), fill='red')
c.create_window(300, 230, window=text_1)

c.create_text(300, 270, text='PASSWORD', font=('Verdana', 20), fill='red')
c.create_window(300, 300, window=text_2)

c.create_window(300, 360, window=btn1)
c.create_window(300, 385, window=btn2, tag='new_btn')

root.mainloop()
