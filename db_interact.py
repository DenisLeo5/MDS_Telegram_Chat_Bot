import sqlite3


def get_new_id(table):
    connect = sqlite3.connect('mds_db.sqlite')
    cursor = connect.cursor()
    cursor.execute(f'SELECT id FROM {table}')
    try:
        new_id = max(cut_info(cursor.fetchall())) + 1
    except Exception:
        new_id = 0
    connect.commit()
    return new_id


def get_chat_id(chat_id):
    connect = sqlite3.connect('mds_db.sqlite')
    cursor = connect.cursor()
    cursor.execute(f'SELECT id FROM chat_table WHERE chat_id = {chat_id}')
    chat_id = cut_info(cursor.fetchall())[0]
    connect.commit()
    return chat_id


def cut_info(info, mode=None):
    if type(info) == list:
        if mode == 'str':
            return [cut_info(i, 'str') for i in info]
        return [cut_info(i) for i in info]
    else:
        if mode == 'str':
            return list(info)[0].replace("'", '')
        return list(info)[0]


def check_chat_existence(chat_id):
    connect = sqlite3.connect('mds_db.sqlite')
    cursor = connect.cursor()
    cursor.execute(f'SELECT chat_id FROM chat_table')
    connect.commit()
    return chat_id in cut_info(cursor.fetchall())


def add_chat(chat_id):
    connect = sqlite3.connect('mds_db.sqlite')
    cursor = connect.cursor()
    cursor.execute(f'INSERT INTO chat_table VALUES (?, ?)', (get_new_id('chat_table'), chat_id))
    connect.commit()


def check_user_existence(chat_id, user_id):
    connect = sqlite3.connect('mds_db.sqlite')
    cursor = connect.cursor()
    chat_id = get_chat_id(chat_id)
    cursor.execute(f'SELECT user_id FROM user_table WHERE chat_id = {chat_id}')
    connect.commit()
    return user_id in cut_info(cursor.fetchall())


def add_user_to_chat(chat_id, user_id):
    connect = sqlite3.connect('mds_db.sqlite')
    cursor = connect.cursor()
    chat_id = get_chat_id(chat_id)
    cursor.execute(f'INSERT INTO user_table VALUES (?, ?, ?, ?)', (chat_id, user_id, 50, 1))
    connect.commit()


def delete_user_from_chat(chat_id, user_id):
    connect = sqlite3.connect('mds_db.sqlite')
    cursor = connect.cursor()
    chat_id = get_chat_id(chat_id)
    cursor.execute(f'DELETE FROM user_table WHERE chat_id = {chat_id}, user_id = {user_id}')
    connect.commit()


def get_user_info(chat_id, user_id):
    connect = sqlite3.connect('mds_db.sqlite')
    cursor = connect.cursor()
    chat_id = get_chat_id(chat_id)
    cursor.execute(f'SELECT daily_faith, count_messages FROM user_table WHERE chat_id = {chat_id} AND user_id = {user_id}')
    info = cut_info(cursor.fetchall())
    connect.commit()
    return info


def add_message(chat_id, user_id):
    connect = sqlite3.connect('mds_db.sqlite')
    cursor = connect.cursor()
    chat_id = get_chat_id(chat_id)
    cursor.execute(f'SELECT count_messages FROM user_table WHERE chat_id = {chat_id} AND user_id = {user_id}')
    count_messages = cut_info(cursor.fetchall())[0]
    cursor.execute(f'UPDATE user_table SET messages = {count_messages + 1} WHERE chat_id = {chat_id} AND user_id = {user_id}')
    connect.commit()


def get_data(chat_id):
    pass
