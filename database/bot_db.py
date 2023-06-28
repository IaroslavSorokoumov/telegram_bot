
import sqlite3

def add_response_to_db(hotel_data: dict) -> None:
    """таблица с данными об отеле, которую выдали пользователю"""

    connect = sqlite3.connect('database/history.db')
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS hotel(
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
    connect.commit()

    cursor.execute("INSERT INTO hotel (chat_id, city_name, hotel_id, hotel_name, hotel_price, common_price, hotel_address, hotel_days, hotel_location) "
                      "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (hotel_data['chat_id'], hotel_data['city_name'],hotel_data['hotel_id'], hotel_data['hotel_name'], hotel_data['hotel_price'],
                       hotel_data['common_price'], hotel_data['hotel_address'], hotel_data['hotel_days'], hotel_data['hotel_location'])
                      )
    connect.commit()
    connect.close()


def get_hotel_from_db(chat_id: int) -> (list, None):
    """получение информации из базы данных по запросу history
    список из данных"""


    connect = sqlite3.connect('database/history.db')

    try:
        cursor = connect.cursor()
        cursor.execute(f"""SELECT * FROM hotel WHERE chat_id = '{chat_id}'""")
        hotels_data = cursor.fetchall()
        connect.close()
        return hotels_data

    except sqlite3.OperationalError:
        connect.close()
        return None



