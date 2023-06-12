from telebot.types import Message
from telebot import types
from loader import bot
from states.custom_answers import UserAnswers
import keyboards.reply.answers as answ
import re
from .requests_to_api import city_request
from keyboards.inline.city_keyboard import city_keybord
from .calendar import date_selection
import datetime
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP


@bot.message_handler(commands=["lowprice"])
def lowprice(m: Message) -> None:
    """функция обработки запроса /lowprice. Ловим ответ пользователя - город для поиска отеля"""

    bot.set_state(m.from_user.id, UserAnswers.city, m.chat.id)
    bot.send_message(m.from_user.id, text='Какой город вас интересует? ')


@bot.message_handler(state=UserAnswers.city)
def get_city_name(m: Message) -> None:
    """Делаем запрос к API и получаем список городов"""
    city_name = m.text.lower()
    if m.text.isalpha():
        city_data = city_request(city_name) # функция получения словаря с городами - "ИМЯ": "id"
        city_keybord(m, city_data)          # обращаюсь к функции с inline клавишами, где на клавишах имена городов, а ответ id города
        bot.set_state(m.from_user.id, UserAnswers.city_id, m.chat.id) # записываю id город в состояние пользователя и передаю для записи в data

        with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
            data['city'] = m.text
    else:
        bot.reply_to(m, "Ошибка в написании города. Должны быть только буквы")

@bot.callback_query_handler(func=None, state=UserAnswers.city_id)
def get_city_id(call):
    """Получаем ID города и записываем в состояние.
    Спрашиваю про кол-во отелей"""

    city_id = call.data # Id города в сообщении от кнопки
    bot.send_message(call.from_user.id, f"ID города = {city_id}") # чтобы проверить Id при тесте в боте
    bot.send_message(call.from_user.id, 'Отлично. Cколько отелей хотите просмотреть (не более 5)?', reply_markup=answ.request_hotels())
    # получаю ответ по клавишам с цифрами - функция request_hotels
    bot.set_state(call.from_user.id, UserAnswers.hotel_qty, call.message.chat.id)

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['city_id'] = int(city_id)


@bot.message_handler(state=UserAnswers.hotel_qty)
def get_hotel_qty(m: Message) -> None:
    """Записываем кол-во отелей в состояние пользователя и спрашиваем про фото отелей"""

    if m.text.isdigit() and 0 < int(m.text) < 6:
        bot.reply_to(m, 'Принято. Нужно ли подгрузить фото отелей. Выберите клавишу Да/Нет?', reply_markup=answ.request_yes_no())
        bot.set_state(m.from_user.id, UserAnswers.photo, m.chat.id)

        with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
            data['hotel_qty'] = m.text
    else:
        bot.reply_to(m, "Ошибка. Только цифры и не более 5")


@bot.message_handler(state=UserAnswers.photo)
def get_photo(m: Message) -> None:
    """Записываем кол-во отелей в состояние пользователя и задаём след. вопрос"""

    if m.text.lower() == 'да':
        bot.reply_to(m, 'Спасибо. Сколько фото показать (не более 3-х)? Нажмите нужную клавишу', reply_markup=answ.request_photo())
        bot.set_state(m.from_user.id, UserAnswers.photo_qty, m.chat.id)

        with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
            data['photo'] = m.text

    elif m.text.lower() == 'нет':

        with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
            data['photo'] = m.text

        bot.send_message(m.from_user.id, 'Теперь необходимо выбрать дату заезда.')
        bot.set_state(m.from_user.id, UserAnswers.check_in, m.chat.id)

    else:
        bot.reply_to(m, "Ошибка. Только ответ Да или Нет")


@bot.message_handler(state=UserAnswers.photo_qty)
def get_photo_qty(m: Message) -> None:
    """Записываю кол-во нужных фото в данные запроса"""

    if m.text.isdigit() and 0 < int(m.text) < 4:

        with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
            data['photo_qty'] = int(m.text)

        bot.reply_to(m, 'Теперь необходимо выбрать дату заезда.')
        calendar, step = DetailedTelegramCalendar(locale='ru', min_date=datetime.date.today()).build()
        bot.send_message(m.chat.id,
                         f"Выберите {LSTEP[step]}",
                         reply_markup=calendar)
        bot.set_state(m.from_user.id, UserAnswers.check_in, m.chat.id)

    else:
        bot.reply_to(m, 'Ошибка в количестве фото, не менее 1 и не более 3-х')

@bot.callback_query_handler(func=DetailedTelegramCalendar.func(), state=UserAnswers.check_in)
def cal(c):
    result, key, step = DetailedTelegramCalendar(locale='ru', min_date=datetime.date.today()).process(c.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                                c.message.chat.id,
                                c.message.message_id,
                                reply_markup=key)
    elif result:
        bot.edit_message_text(f"Ваш дата заезда: {result}",
                                c.message.chat.id,
                                c.message.message_id)
        bot.send_message(c.from_user.id, "Отлично, теперь выберите дату выезда")
        with bot.get_state(c.from_user.id, c.message.chat.id) as data:
            date = data['check_in']
        calendar, step = DetailedTelegramCalendar(locale='ru', min_date=date).build()
        bot.send_message(c.message.chat.id,
                         f"Выберите {LSTEP[step]}",
                         reply_markup=calendar)
        bot.set_state(c.from_user.id, UserAnswers.check_out, c.message.chat.id)

        with bot.retrieve_data(c.from_user.id, c.message.chat.id) as data:
            data['check_in'] = result


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(), state=UserAnswers.check_out)
def cal(c):
    with bot.get_state(c.from_user.id, c.message.chat.id) as data:
        date = data['check_in']
    result, key, step = DetailedTelegramCalendar(locale='ru', min_date=date).process(c.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                                c.message.chat.id,
                                c.message.message_id,
                                reply_markup=key)
    elif result:
        bot.edit_message_text(f"Ваш дата выезда: {result}",
                                c.message.chat.id,
                                c.message.message_id)

        with bot.retrieve_data(c.from_user.id, c.message.chat.id) as data:
            data['check_out'] = result

    bot.send_message(c.from_user.id, "Спасибо, ищу варианты отелей")
    bot.reply_to(c.from_user.id, f"Данные запроса: {data}")
