import sqlite3
from handlers import client
from handlers import qiwi

def sql_start():
    global connect, cursor
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    if cursor:
       print('Database connected OK!')
    cursor.execute('CREATE TABLE IF NOT EXISTS database(id INTEGER, password, admin, api, number)')
    connect.commit()

async def sql_add_command(state):
    cursor.execute(f'SELECT id FROM database WHERE id = {client.people_id}')
    global data
    data = cursor.fetchone()
    connect.commit()
    if data is None:
        cursor.execute('INSERT INTO database VALUES(?, ?, ?, ?, ?)', (client.people_id, '0', '0', '0', '0'))
        connect.commit()


async def update_api():
    cursor.execute('UPDATE database SET api == ? WHERE id == ?', (qiwi.api_text, qiwi.people_id))
    connect.commit()

async def update_number():
    cursor.execute('UPDATE database SET number == ? WHERE id == ?', (qiwi.number_text, qiwi.people_id))
    connect.commit()


def cursor():
    return None


def data():
    return None