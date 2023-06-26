
import sqlite3


def add_bot_user(chat_id: int, user_name: str) -> None:
    """функция добавления записи о пользователе в базу данных.
     Создаёт таблицу для пользователя с его данными"""

    connect_to_db = sqlite3.connect('database/users_history.db')
    cursor_db = connect_to_db.cursor()
    cursor_db.execute("""CREATE TABLE IF NOT EXISTS user(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                chat_id INTEGER UNIQUE,
                user_name STRING);
                """)
    connect_to_db.commit()

    try:
        cursor_db.execute(
            "INSERT INTO user (chat_id, user_name) VALUES (?, ?)",
            (chat_id, user_name)
        )

        connect_to_db.commit()
        connect_to_db.close()
    except sqlite3.IntegrityError:
        connect_to_db.close()

def add_response_to_db(hotel_data: dict) -> None:
    """таблица с данными об отеле, которую выдали пользователю"""

    connect_to_db = sqlite3.connect('database/response_history.db')
    cursor_db = connect_to_db.cursor()
    cursor_db.execute("""CREATE TABLE IF NOT EXISTS hotel(
                      id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                      chat_id INTEGER,
                      city_name STRING,
                      hotel_id INTEGER,
                      hotel_name STRING,
                      hotel_price REAL,
                      common_price REAL,
                      hotel_address TEXT,
                      hotel_days REAL,
                      hotel_location REAL);
    """)
    connect_to_db.commit()
    cursor_db = connect_to_db.cursor()
    cursor_db.execute("INSERT INTO hotel (chat_id, city_name, hotel_id, hotel_name, hotel_price, common_price, hotel_address, hotel_days, hotel_location) "
                      "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (hotel_data['chat_id'], hotel_data['city_name'],hotel_data['hotel_id'], hotel_data['hotel_name'], hotel_data['hotel_price'],
                       hotel_data['common_price'], hotel_data['hotel_address'], hotel_data['hotel_days'], hotel_data['hotel_location'])
                      )
    connect_to_db.commit()
    connect_to_db.close()


def get_hotel_from_db(chat_id: int) -> list:
    """получение информации из базы данных по запросу history
    список из данных"""


    connect_to_db = sqlite3.connect('database/response_history.db')

    try:
        cursor_db = connect_to_db.cursor()
        cursor_db.execute(f"""SELECT * FROM hotel WHERE chat_id = '{chat_id}'""")
        hotels_data = cursor_db.fetchall()
        connect_to_db.close()
        return hotels_data

    except sqlite3.OperationalError:
        connect_to_db.close()



