from loader import bot
from telebot.types import Message


@bot.message_handler(commands=['hello-world'])
def hello_world(message: Message):
    mess = "The world of Python welcomes you to this chatbot!"
    bot.send_message(message.chat.id, mess)