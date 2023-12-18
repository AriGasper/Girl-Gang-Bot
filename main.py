import telebot
from telebot import types
import sqlite3

bot = telebot.TeleBot('6379060038:AAEiac4aMyNUtPYxdrBTb2_BbHPiwM5LjDE');

name = None
age = None
town = None

@bot.message_handler(commands=['start'])
def main(message):

    global tel_id
    tel_id = message.from_user.id

    butnAnketa = types.ReplyKeyboardMarkup()
    butnAnkCreate = types.KeyboardButton('Создать анкету🙋‍♀️')
    butnAnketa.row(butnAnkCreate)

    if is_id_in_database(message.chat.id):
        bot.send_message(message.chat.id, 'С возвращением! Отправь любое сообщение для продолжения', reply_markup=butnAnketa)
        bot.register_next_step_handler(message, done_anketa)

    else:
        bot.send_message(message.chat.id, 'Приветик, подружка!💘', reply_markup=butnAnketa)
        bot.register_next_step_handler(message, create_click)



def is_id_in_database(user_id):
    conn = sqlite3.connect('girlgang1.db')
    cur = conn.cursor()

    user_id = "SELECT id FROM users WHERE telegram_id = ?"
    cur.execute(user_id, (tel_id,))

    result = cur.fetchone()
    conn.close()
    is_in_db = result[0] if result else None

    return is_in_db
def create_click(message):
    if message.text == 'Создать анкету🙋‍♀️':
        bot.send_message(message.chat.id, 'Конечно, сейчас тебя зарегистрируем)\n Введи, пожалуйста, свое имя')
        bot.register_next_step_handler(message, create_name)
    if message.text == 'Найти подружку':
        bot.register_next_step_handler(message, anketa)



def create_name(message):
    global name

    name = message.text.strip()

    bot.send_message(message.chat.id, 'Приятно познакомиться, '+ message.text + '! Сколько тебе лет?')
    bot.register_next_step_handler(message, create_age)

def create_age(message):
    global age
    age = message.text.strip()
    bot.send_message(message.chat.id, 'Супер!Напиши цифру, из какого ты города:\n1. Москва\n2.Санкт-Петербург\n3.Другой город')
    bot.register_next_step_handler(message, create_town)

def create_town(message):
    global town
    town = message.text.strip()
    bot.send_message(message.chat.id, 'Класс! Напиши номера своих увлечений: \n1. Классическая музыка\n2. Современная музыка\n3. Растения\n4. Животные\n5. Рисование и творчество\n6. Рукоделие\n7. Еда и кулинария\n8. Театр')
    bot.register_next_step_handler(message, create_hobbies)

def create_hobbies(message):
    global hobbies
    hobbies = message.text.strip()
    conn = sqlite3.connect('girlgang1.db')
    cur = conn.cursor()

    cur.execute("INSERT INTO users(telegram_id, name, age, town_id) VALUES ('%s','%s','%s','%s')" % (message.chat.id,name, age, town))
    conn.commit()

    users_id = cur.execute("SELECT id FROM users WHERE telegram_id = '%s'" %(message.chat.id)).fetchone()[0]


    for hobby in hobbies:
        cur.execute("INSERT INTO users_hobbies(user_id,hobby_id) VALUES ('%s','%s')" % (users_id, hobby))
    conn.commit()

    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Отправь любое сообщение, чтобы продолжить')
    bot.register_next_step_handler(message, done_anketa)

def get_user_hobbies(cur_id):
    conn = sqlite3.connect('girlgang1.db')
    cur = conn.cursor()

    hobby_ids = cur.execute( "SELECT hobby_id FROM users_hobbies WHERE user_id = '%s'" % (cur_id)).fetchall()



    cur_hobby_names = []
    for hobby_id in hobby_ids:
        # Получение названий хобби по каждому hobby_id
        cur.execute("SELECT name FROM hobbies WHERE id = ?", (hobby_id[0],))
        hobby_name = cur.fetchone()[0]
        cur_hobby_names.append(hobby_name)
    conn.close()
    return cur_hobby_names
def done_anketa(message):
    conn = sqlite3.connect('girlgang1.db')
    cur = conn.cursor()
    cur_name = cur.execute("SELECT name FROM users WHERE telegram_id = '%s'" % (message.chat.id)).fetchone()[0]
    cur_age = cur.execute("SELECT age FROM users WHERE telegram_id = '%s'" % (message.chat.id)).fetchone()[0]
    cur_town_id = cur.execute("SELECT town_id FROM users WHERE telegram_id = '%s'" % (message.chat.id)).fetchone()[0]
    cur_town = cur.execute("SELECT name FROM towns WHERE id = '%s'" % (cur_town_id)).fetchone()[0]
    cur_id = cur.execute("SELECT id FROM users WHERE telegram_id = '%s'" % (message.chat.id)).fetchone()[0]
    cur_hobby_name =  ', '.join(get_user_hobbies(cur_id))

    bot.send_message(message.chat.id, 'Твоя анкета:\nИмя: ' + cur_name + '\nВозраст: ' + str(cur_age) + '\nГород: ' + cur_town + '\nХобби: ' + cur_hobby_name)
    bot.send_message(message.chat.id, 'Супер, ты зарегистрирована!\nДержи эксклюзивный стикерпак от GirlGang🤩\nПриступим к поиску подруги?')
    # Отправка стикера
    sticker_file_id = 'CAACAgIAAxkBAAEK-65lfwJn-l9XAAFtvfYqp4iYIXMYrksAAnU6AANO8UsClcyQOMc3YTME'
    bot.send_sticker(message.chat.id, sticker=sticker_file_id)
    cur.close()
    conn.close()

    butnAnketa = types.ReplyKeyboardMarkup()

    butnAnkWatch = types.KeyboardButton('Найти подружку')
    butnAnketa.row(butnAnkWatch)

    bot.send_message(message.chat.id, 'Отправь любое сообщение для начала поиска))', reply_markup=butnAnketa)
    bot.register_next_step_handler(message, create_click)

def get_other_users(cur_id, cur_town):
    # Подключение к базе данных
    conn = sqlite3.connect('girlgang1.db')
    cur = conn.cursor()

    others_ids = cur.execute( "SELECT telegram_id FROM users WHERE telegram_id != '%s'" % (cur_id)).fetchall()

    # Закрытие соединения

    conn.close()
    return others_ids
stop = False
popa = 2

@bot.message_handler(content_types=['text'])
def anketa(message):
    global other_id

    conn = sqlite3.connect('girlgang1.db')
    cur = conn.cursor()

    cur_town_id = cur.execute("SELECT town_id FROM users WHERE telegram_id = '%s'" % (message.chat.id)).fetchone()[0]
    cur_town = cur.execute("SELECT name FROM towns WHERE id = '%s'" % (cur_town_id)).fetchone()[0]


    user = cur.execute("""
                SELECT 
                    users.id AS user_id,
                    users.name AS user_name,
                    users.age AS user_age,
                    towns.name AS town_name,
                    GROUP_CONCAT(hobbies.name, ', ') AS hobbies
                FROM 
                    users
                JOIN 
                    towns ON users.town_id = towns.id
                LEFT JOIN 
                    users_hobbies ON users.id = users_hobbies.user_id
                LEFT JOIN 
                    hobbies ON users_hobbies.hobby_id = hobbies.id
                WHERE 
                    users.town_id = (SELECT town_id FROM users WHERE telegram_id = ?)
                    AND users.telegram_id != ?
                    AND NOT EXISTS (
                        SELECT 1
                        FROM matches
                        WHERE (matches.user_from = (SELECT id FROM users WHERE telegram_id = ?) AND matches.user_to = users.id)
                           OR (matches.user_from = users.id AND matches.user_to = (SELECT id FROM users WHERE telegram_id = users.telegram_id))
                           AND (matches.user_from != users.id OR matches.user_to != (SELECT id FROM users WHERE telegram_id = users.telegram_id))
                    )
                GROUP BY 
                    users.id;
            """, (message.chat.id, message.chat.id, message.chat.id)).fetchall()
    if not user:
        bot.reply_to(message, "Возвращайся еще!")
    else:
        other_id = user[0][0]
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('like', callback_data='like')
        btn2 = types.InlineKeyboardButton('dislike', callback_data='dislike')
        btn3 = types.InlineKeyboardButton('stop', callback_data='stop')
        markup.row(btn1, btn2, btn3)
        bot.reply_to(message, 'Анкета:\nИмя: ' + str(user[0][1]) + '\nВозраст: ' + str(user[0][2]) + '\nГород: ' + str(user[0][3]) + '\nХобби: ' + str(user[0][4]), reply_markup=markup )

    cur.close()
    conn.close()


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global other_id
    global i
    global current_place_index
    i = 0
    conn = sqlite3.connect('girlgang1.db')
    cur = conn.cursor()
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('like', callback_data='like')
    btn2 = types.InlineKeyboardButton('dislike', callback_data='dislike')
    btn3 = types.InlineKeyboardButton('stop', callback_data='stop')
    markup.row(btn1, btn2, btn3)
    id = cur.execute("SELECT id FROM users WHERE telegram_id = '%s'" % (callback.message.chat.id)).fetchone()[0]

    if callback.data == 'place':
        town_id_1 = cur.execute("SELECT town_id FROM users WHERE telegram_id = '%s'" % (tel_id)).fetchone()[0]
        hobby_ids = cur.execute( "SELECT hobby_id FROM users_hobbies WHERE user_id = '%s'" % (tel_id)).fetchall()

        places_result = cur.execute( "SELECT description FROM places WHERE town_id = ?  and hobby_id = ? ", (town_id_1, 5)).fetchall()
        places = [place[0] for place in places_result]
        # Отправляем текстовое сообщение со списком мест
        for place in places:
            bot.send_message(callback.message.chat.id, '\n{}'.format(place))


    if callback.data == 'like':
        cur.execute("INSERT INTO matches(user_from, user_to, liked) VALUES ('%s','%s','%s')" % (id, other_id, 1))
        conn.commit()
        matched = cur.execute("""
        SELECT DISTINCT 
            m1.user_to AS matched_user_id
            FROM
            matches m1
            JOIN
            matches m2 ON m1.user_from = m2.user_to
             AND m1.user_to = m2.user_from
            WHERE
             m1.liked = 1
            AND m2.liked = 1
            AND m1.user_from = (SELECT id FROM users WHERE telegram_id = ?);""",  (callback.message.chat.id,)).fetchall()

        if matched:
            markup1 = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton('Подобрать место', callback_data='place')
            markup1.row(btn)
            matched_id = cur.execute("SELECT telegram_id FROM users WHERE id = '%s'" % (str(matched[0][i]))).fetchone()[0]
            i = i + 1
            bot.reply_to(callback.message, "У вас мэтч с tg://user?id=" +  str(matched_id), reply_markup=markup1 )



        user = cur.execute("""
            SELECT 
                users.id AS user_id,
                users.name AS user_name,
                users.age AS user_age,
                towns.name AS town_name,
                GROUP_CONCAT(hobbies.name, ', ') AS hobbies
            FROM 
                users
            JOIN 
                towns ON users.town_id = towns.id
            LEFT JOIN 
                users_hobbies ON users.id = users_hobbies.user_id
            LEFT JOIN 
                hobbies ON users_hobbies.hobby_id = hobbies.id
            WHERE 
                users.town_id = (SELECT town_id FROM users WHERE telegram_id = ?)
                AND users.telegram_id != ?
                AND NOT EXISTS (
                    SELECT 1
                    FROM matches
                    WHERE (matches.user_from = (SELECT id FROM users WHERE telegram_id = ?) AND matches.user_to = users.id)
                       OR (matches.user_from = users.id AND matches.user_to = (SELECT id FROM users WHERE telegram_id = users.telegram_id))
                       AND (matches.user_from != users.id OR matches.user_to != (SELECT id FROM users WHERE telegram_id = users.telegram_id))
                )
            GROUP BY 
                users.id;
        """, (callback.message.chat.id, callback.message.chat.id, callback.message.chat.id)).fetchall()

        if not user:
            bot.reply_to(callback.message, "Возвращайся еще!")
        else:
            other_id = user[0][0]
            bot.reply_to(callback.message, 'Анкета:\nИмя: ' + str(user[0][1]) + '\nВозраст: ' + str(user[0][2]) + '\nГород: ' + str(user[0][3]) + '\nХобби: ' + str(user[0][4]), reply_markup=markup)

    elif callback.data == 'dislike':

        cur.execute("INSERT INTO matches(user_from, user_to, liked) VALUES ('%s','%s','%s')" % (id, other_id, 0))
        conn.commit()
        user = cur.execute("""
                    SELECT 
                        users.id AS user_id,
                        users.name AS user_name,
                        users.age AS user_age,
                        towns.name AS town_name,
                        GROUP_CONCAT(hobbies.name, ', ') AS hobbies
                    FROM 
                        users
                    JOIN 
                        towns ON users.town_id = towns.id
                    LEFT JOIN 
                        users_hobbies ON users.id = users_hobbies.user_id
                    LEFT JOIN 
                        hobbies ON users_hobbies.hobby_id = hobbies.id
                    WHERE 
                        users.town_id = (SELECT town_id FROM users WHERE telegram_id = ?)
                        AND users.telegram_id != ?
                        AND NOT EXISTS (
                            SELECT 1
                            FROM matches
                            WHERE (matches.user_from = (SELECT id FROM users WHERE telegram_id = ?) AND matches.user_to = users.id)
                               OR (matches.user_from = users.id AND matches.user_to = (SELECT id FROM users WHERE telegram_id = users.telegram_id))
                               AND (matches.user_from != users.id OR matches.user_to != (SELECT id FROM users WHERE telegram_id = users.telegram_id))
                        )
                    GROUP BY 
                        users.id;
                """, (callback.message.chat.id, callback.message.chat.id, callback.message.chat.id)).fetchall()
        if not user:
            bot.reply_to(callback.message, "Возвращайся еще!")
        else:
            other_id = user[0][0]
            bot.reply_to(callback.message,
                         'Анкета:\nИмя: ' + str(user[0][1]) + '\nВозраст: ' + str(user[0][2]) + '\nГород: ' + str(
                             user[0][3]) + '\nХобби: ' + str(user[0][4]), reply_markup=markup)
    cur.close()
    conn.close()
    return True

if __name__ == "__main__":
    bot.polling(none_stop=True)


