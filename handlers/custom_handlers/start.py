from telebot.types import Message
from loader import bot


@bot.message_handler(commands=["start"])
def bot_start(message: Message):
    """Запуск бота и приветствие"""
    text = "\nЭтот бот поможет с выбором лучших отелей и цен.\n Для вывода справки по командам - /help"
    bot.reply_to(message, f"Привет, {message.from_user.full_name}! {text}")