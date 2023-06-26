from telebot.types import Message
from database.bot_db import add_bot_user
from loader import bot

@bot.message_handler(commands=["help"])
def bot_help(m: Message):
    chat_id = m.from_user.id
    user_name = m.from_user.username
    user_fullname = m.from_user.full_name
    add_bot_user(chat_id=chat_id,
                 user_name=user_name,
                 )
    text = "/help — помощь по командам бота,\n" \
           "/lowprice — вывод самых дешёвых отелей в городе,\n" \
           "/highprice — вывод самых дорогих отелей в городе,\n" \
           "/bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра.\n" \
           "/history — вывод истории поиска отелей"
    bot.send_message(m.chat.id, text)
