import sqlite3

conn = sqlite3.connect('details.db')
cursor = conn.cursor()


def view_data():
    for i in cursor.execute('SELECT * FROM accounts'):
        print(i)


def create_table():
    cursor.execute('''CREATE TABLE accounts(
        user_name TEXT,
        password TEXT,
        tt_win INTEGER,
        tt_loss INTEGER,
        tt_draw INTEGER,
        ch_win INTEGER,
        ch_loss INTEGER,
        ch_draw INTEGER,
        sh_win INTEGER,
        sh_loss INTEGER,
        sh_draw INTEGER,
        PRIMARY KEY (user_name));''')


def delete_data():
    cursor.execute('DELETE FROM accounts')



conn.commit()
view_data()

conn.close()
