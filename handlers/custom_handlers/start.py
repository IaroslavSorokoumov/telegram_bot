from telebot.types import Message
from loader import bot


@bot.message_handler(commands=["start"])
def bot_start(m: Message):
    """Запуск бота и приветствие"""

    text = "\nЭтот бот поможет с выбором лучших отелей и цен.\n " \
           "Для вывода справки по командам - нажмите или введите команду /help"
    bot.reply_to(m, f"Привет, {m.from_user.full_name}! {text}")