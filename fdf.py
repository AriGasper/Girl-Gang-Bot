import sqlite3

conn = sqlite3.connect('girlgang1.db') #создание бд
cur = conn.cursor()

    #создание таблицы с пользователями
cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50), age varchar(20), town varchar(50), hobbies varchar(50))')
conn.commit()
conn.close()