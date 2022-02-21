import socket
import json
import threading
import sqlite3
import chat_server
import config


connected = []
available = []

user_data = []
port = 8081
ip = config.get_ip()

def read_data_from_db():
    global user_data
    connection = sqlite3.connect('details.db')
    cursor = connection.cursor()
    for record in cursor.execute('SELECT * FROM accounts'):
        user_data.append(record[:2])
    connection.close()


def start_personal_chat_server(port):
    chat_server.ChatServerIndividual(port)


def search_rank(records, user_name):
    rank = 0
    for record in records:
        rank += 1
        if record[0] == user_name:
            break
    return rank


def get_rank(user_name):
    connection = sqlite3.connect('details.db')
    cursor = connection.cursor()

    rank_data = []
    ch_data = list(cursor.execute(
        'SELECT user_name, ch_win, ch_loss, ch_draw FROM accounts ORDER BY ch_win DESC, ch_draw DESC, ch_loss ASC;'))
    rank_data.append(search_rank(ch_data, user_name))
    rank_data.append(ch_data[rank_data[-1] - 1])
    tt_data = list(cursor.execute(
        'SELECT user_name, tt_win, tt_loss, tt_draw FROM accounts ORDER BY tt_win DESC, tt_draw DESC, tt_loss ASC;'))
    rank_data.append(search_rank(tt_data, user_name))
    rank_data.append(tt_data[rank_data[-1] - 1])
    sh_data = list(cursor.execute(
        'SELECT user_name, sh_win, sh_loss, sh_draw FROM accounts ORDER BY sh_win DESC, sh_draw DESC, sh_loss ASC;'))
    rank_data.append(search_rank(sh_data, user_name))
    rank_data.append(sh_data[rank_data[-1] - 1])

    rank_data.append('rank_info')
    cursor.close()
    return rank_data


def client_receiving(client_num):
    global port
    while True:
        try:
            data = json.loads(connected[client_num][0].recv(4096).decode('utf-8'))
        except json.JSONDecodeError:
            data = 'wait'
        if data == 'send_user_list':
            active_clients = []
            for client in connected:
                if client[0]:
                    active_clients.append(client[1])
            active_clients.append('user_list')
            connected[client_num][0].send(json.dumps(active_clients).encode('utf-8'))
        elif 'connection_request' in data:
            index = int(data.split(' ')[1])
            temp = index

            incorrect = False
            while not (connected[temp][0] and temp != client_num):
                temp += 1
                if temp == len(connected):
                    connected[client_num][0].send(json.dumps('chat_rejected ' + data.split(' ')[2]).encode('utf-8'))
                    incorrect = True
                    break
            if incorrect: continue
            if connected[temp][1] != data.split(' ')[2]:
                connected[client_num][0].send(json.dumps('chat_rejected ' + data.split(' ')[2]).encode('utf-8'))
                continue
            connected[temp][0].send(
                json.dumps('chat_request ' + connected[client_num][1] + ' ' + str(client_num)).encode('utf-8'))
        elif 'rejected ' in data:
            connected[int(data.split(' ')[1])][0].send(
                json.dumps('chat_rejected ' + connected[client_num][1]).encode('utf-8'))
        elif 'accepted ' in data:
            threading.Thread(target=lambda: start_personal_chat_server(port)).start()
            connected[int(data.split(' ')[1])][0].send(
                json.dumps('chat_accepted ' + connected[client_num][1]).encode('utf-8'))
            connected[int(data.split(' ')[1])][0].send(json.dumps('conn_data ' + str(port)).encode('utf-8'))
            connected[client_num][0].send(json.dumps('conn_data ' + str(port)).encode('utf-8'))
            port += 1
        elif '**||CLOSE||**' == data:
            connected[client_num][0].close()
            connected[client_num][0] = None
            break
        elif '**||RANK||** ' in data:
            data = get_rank(data.split(' ')[1])
            connected[client_num][0].send(json.dumps(data).encode('utf-8'))


def find_champs():
    connection = sqlite3.connect('details.db')
    cursor = connection.cursor()

    ch_data = list(cursor.execute(
        'SELECT user_name, ch_win, ch_loss, ch_draw FROM accounts ORDER BY ch_win DESC, ch_draw DESC, ch_loss ASC;'))[0]
    tt_data = list(cursor.execute(
        'SELECT user_name, tt_win, tt_loss, tt_draw FROM accounts ORDER BY tt_win DESC, tt_draw DESC, tt_loss ASC;'))[0]
    sh_data = list(cursor.execute(
        'SELECT user_name, sh_win, sh_loss, sh_draw FROM accounts ORDER BY sh_win DESC, sh_draw DESC, sh_loss ASC;'))[0]

    cursor.close()

    champ_data = [ch_data, tt_data, sh_data, 'champions']
    return champ_data


def check_connection(conn):
    id, password = json.loads(conn[0].recv(4096).decode('utf-8'))

    if id[:3] == ' **':
        for record in user_data:
            if id[3:] == record[0]:
                conn[0].send(json.dumps('taken').encode('utf-8'))
                threading.Thread(target=lambda: client_receiving(len(connected) - 1)).start()
                return
        connection = sqlite3.connect('details.db')
        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO accounts VALUES ('{id[3:]}','{password}', 0, 0, 0, 0, 0, 0, 0, 0, 0)")
        connection.commit()
        connection.close()
        connected.append([conn[0], id[3:]])
        user_data.append((id[3:], password, 0, 0, 0))
        available.append(len(user_data) - 1)
        conn[0].send(json.dumps('ok').encode('utf-8'))
        champs = find_champs()
        conn[0].send(json.dumps(champs).encode('utf-8'))

        threading.Thread(target=lambda: client_receiving(len(connected) - 1)).start()
    else:
        for record in user_data:
            if record[0] == id and record[1] == password:
                conn[0].send(json.dumps('ok').encode('utf-8'))
                champs = find_champs()
                conn[0].send(json.dumps(champs).encode('utf-8'))
                connected.append([conn[0], id])
                available.append(user_data.index(record))
                threading.Thread(target=lambda: client_receiving(len(connected) - 1)).start()
                return
        conn[0].send(json.dumps('incorrect').encode('utf-8'))
        conn[0].close()


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((ip, 8080))
sock.listen(5)

read_data_from_db()

while True:
    guest = sock.accept()
    check_connection(guest)
