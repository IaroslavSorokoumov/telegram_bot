from telebot.types import Message
from loader import bot

@bot.message_handler(commands=["help"])
def bot_help(m: Message):

    text = "/help — помощь по командам бота,\n" \
           "/lowprice — вывод самых дешёвых отелей в городе,\n" \
           "/highprice — вывод самых дорогих отелей в городе,\n" \
           "/bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра.\n" \
           "/history — вывод истории поиска отелей.\n" \
           "<b>Название города можно вводить как на русском, так и на английском языках!</b>"
    bot.send_message(m.chat.id, text, parse_mode='html')
