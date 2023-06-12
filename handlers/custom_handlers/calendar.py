import datetime

from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from loader import bot
from telebot.types import Message
from states.custom_answers import UserAnswers

LSTEP_RU: dict[str, str] = {'y': 'год', 'm': 'месяц', 'd': 'день'}
def date_selection(m: Message):
    """функция календаря - для выбора дат заезда и выезда"""
    calendar, step = DetailedTelegramCalendar(locale='ru', min_date=date).build()
    bot.send_message(m.chat.id,
                     f"Выберите {LSTEP[step]}",
                     reply_markup=calendar)

    @bot.callback_query_handler(func=DetailedTelegramCalendar.func())
    def cal(c) -> str:

        result, key, step = DetailedTelegramCalendar(locale='ru', min_date=date).process(c.data)
        if not result and key:
            bot.edit_message_text(f"Выберите {LSTEP[step]}",
                                  c.message.chat.id,
                                  c.message.message_id,
                                  reply_markup=key)
        elif result:
            bot.edit_message_text(f"Ваш дата: {result}",
                                  c.message.chat.id,
                                  c.message.message_id)
            return result



