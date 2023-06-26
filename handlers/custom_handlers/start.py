from telebot.types import Message
from loader import bot
from database.bot_db import get_hotel_from_db, add_bot_user


@bot.message_handler(commands=["start"])
def bot_start(m: Message):
    """Запуск бота и приветствие"""
    chat_id = m.from_user.id
    user_name = m.from_user.username
    user_fullname = m.from_user.full_name
    add_bot_user(chat_id=chat_id,
                 user_name=user_name,
                 )
    text = "\nЭтот бот поможет с выбором лучших отелей и цен.\n Для вывода справки по командам - /help"
    bot.reply_to(m, f"Привет, {m.from_user.full_name}! {text}")