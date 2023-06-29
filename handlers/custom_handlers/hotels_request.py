import json

from telebot.types import Message, CallbackQuery
from telebot import types
from loader import bot
from states.custom_answers import UserAnswers
import keyboards.reply.answers as answ
import re
from .requests_to_api import city_request, get_hotel_list, get_hotel_details
from keyboards.inline.city_keyboard import city_keybord
from . import history
import datetime
from telegram_bot_calendar import DetailedTelegramCalendar #LSTEP
from handlers.custom_handlers.help import bot_help
from database.bot_db import add_response_to_db

LSTEP: dict[str, str] = {'y': 'год', 'm': 'месяц', 'd': 'день'}
@bot.message_handler(commands=["lowprice", "highprice", "bestdeal"])
def lowprice(m: Message) -> None:
    """функция обработки запроса /lowprice, /highprice и /bestdeal.
    Ловим ответ пользователя - город для поиска отеля
    Записываю начальные состояния юзера"""


    bot.set_state(m.from_user.id, UserAnswers.city, m.chat.id)
    bot.send_message(m.from_user.id, text='Какой город вас интересует? ')

    with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
        data['command'] = m.text[1:]
        data['chat_id'] = m.chat.id
        data['tgram_id'] = m.from_user.id
        data['date_time'] = datetime.datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')

@bot.message_handler(state=UserAnswers.city)
def get_city_name(m: Message) -> None:
    """Делаем запрос к API и получаем список городов"""
    city_name = m.text.lower()
    pattern = r"^[A-Za-z_ -А-Яа-я]*$"
    if re.match(pattern, city_name):
        city_data = city_request(city_name) # функция получения словаря с городами - "Название": "id"
        city_keybord(m, city_data)          # обращаюсь к функции с inline клавишами, где на клавишах имена городов, а ответ id города
        bot.set_state(m.from_user.id, UserAnswers.city_id, m.chat.id) # записываю id город в состояние пользователя и передаю для записи в data


        with bot.retrieve_data(m.from_user.id, m.chat.id) as data: #записываю словарь с городами, чтобы потом в истории поиска вынуть полное имя города
            data['cities_data'] = city_data
    else:
        bot.reply_to(m, "Ошибка в написании города. Должны быть только буквы")

@bot.callback_query_handler(func=None, state=UserAnswers.city_id)
def get_city_id(call: CallbackQuery):
    """Получаем ID города и записываем в состояние.
    Спрашиваю про кол-во отелей"""

    city_id = call.data # Id города в сообщении от кнопки
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        city_data = data['cities_data']
        command = data['command']
    city_name = ""
    for k, v in city_data.items(): # ищу имя города по его Id
        if city_id == v:
            city_name = k
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['city'] = city_name

    if command == 'bestdeal':
        bot.send_message(
            call.from_user.id,
            "Принято. Какая минимальная стоимость отеля за ночь в долларах США вас интересует?"
        )
        bot.set_state(call.from_user.id, UserAnswers.min_price, call.message.chat.id)
    else:
        bot.send_message(call.from_user.id, 'Отлично. Cколько отелей хотите просмотреть (не более 5)?', reply_markup=answ.request_hotels())
        # получаю ответ по клавишам с цифрами - функция request_hotels
        bot.set_state(call.from_user.id, UserAnswers.hotel_qty, call.message.chat.id)

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['city_id'] = int(city_id)


@bot.message_handler(state=UserAnswers.min_price)
def get_min_price(m: Message) -> None:
    if m.text.isdigit():
        bot.send_message(
            m.from_user.id,
            "Отлично. Теперь максимальная стоимость?"
        )
        bot.set_state(m.from_user.id, UserAnswers.max_price, m.chat.id)
        with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
            data['min_price'] = float(m.text)
    else:
        bot.reply_to(m, "Ошибка. Только цифры.")

@bot.message_handler(state=UserAnswers.max_price)
def get_min_price(m: Message) -> None:
    with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
        min_price = data['min_price']

    if m.text.isdigit():
        max_price = float(m.text)
        if max_price >= min_price:
            bot.send_message(
                m.from_user.id,
                "Спасибо. Теперь укажите минимальное расстояние от центра города в км?"
            )
            bot.set_state(m.from_user.id, UserAnswers.min_distance, m.chat.id)
            with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
                data['max_price'] = max_price
        else:
            bot.reply_to(m, "Ошибка. Максимальная цена должна быть больше минимальной.")
    else:
        bot.reply_to(m, "Ошибка. Только цифры.")


@bot.message_handler(state=UserAnswers.min_distance)
def get_min_price(m: Message) -> None:

    if m.text.isdigit():
        bot.send_message(
            m.from_user.id,
            "Отлично. Теперь максимальное расстояние?"
        )
        bot.set_state(m.from_user.id, UserAnswers.max_distance, m.chat.id)
        with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
            data['min_distance'] = float(m.text)
    else:
        bot.reply_to(m, "Ошибка. Только цифры.")


@bot.message_handler(state=UserAnswers.max_distance)
def get_min_price(m: Message) -> None:

    with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
        min_distance = data['min_distance']

    if m.text.isdigit():
        max_distance = float(m.text)
        if max_distance >= min_distance:
            bot.send_message(
                m.from_user.id, 'Отлично. Cколько отелей хотите просмотреть (не более 5)?',
                reply_markup=answ.request_hotels()
            )
            # получаю ответ по клавишам с цифрами - функция request_hotels
            bot.set_state(m.from_user.id, UserAnswers.hotel_qty, m.chat.id)

            with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
                data['max_distance'] = max_distance
        else:
            bot.reply_to(m, "Ошибка. Максимальная расстояние должно быть больше минимального.")
    else:
        bot.reply_to(m, "Ошибка. Только цифры.")
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
            data['photo'] = True

    elif m.text.lower() == 'нет':

        with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
            data['photo'] = False

        bot.send_message(m.from_user.id, 'Теперь необходимо выбрать дату заезда.')
        calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=datetime.date.today()).build()
        bot.send_message(m.chat.id,
                         f"Выберите {LSTEP[step]}",
                         reply_markup=calendar)
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
        calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=datetime.date.today()).build()
        bot.send_message(m.chat.id,
                         f"Выберите {LSTEP[step]}",
                         reply_markup=calendar)
        bot.set_state(m.from_user.id, UserAnswers.check_in, m.chat.id)

    else:
        bot.reply_to(m, 'Ошибка в количестве фото, не менее 1 и не более 3-х')

@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1), state=UserAnswers.check_in)
def calendar(call: CallbackQuery):
    """ловлю ответ по календарю 1 для даты заезда"""
    result, key, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=datetime.date.today()).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                                call.message.chat.id,
                                call.message.message_id,
                                reply_markup=key)
    elif result:
        bot.edit_message_text(f"Ваш дата заезда: {result}",
                                call.message.chat.id,
                                call.message.message_id)
        bot.send_message(call.from_user.id, "Отлично, теперь выберите дату выезда")

        calendar, step = DetailedTelegramCalendar(calendar_id=2, locale='ru', min_date=result).build()
        bot.send_message(call.message.chat.id,
                         f"Выберите {LSTEP[step]}",
                         reply_markup=calendar)
        bot.set_state(call.from_user.id, UserAnswers.check_out, call.message.chat.id)

        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data: # здесь сохраняю только для того чтобы вывести в каллбеке
            data['check_in'] = result

@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2), state=UserAnswers.check_out)
def calendar(call: CallbackQuery):
    """ловлю ответ от календаря 2 по дате выезда """

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data: #дата заезда - как минимальная дата выезда
        date = data['check_in']
        command = data['command']

    result, key, step = DetailedTelegramCalendar(calendar_id=2, locale='ru', min_date=date).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                                call.message.chat.id,
                                call.message.message_id,
                                reply_markup=key)
    elif result:
        bot.edit_message_text(f"Ваш дата выезда: {result}",
                                call.message.chat.id,
                                call.message.message_id)
        date_format = "%d-%m-%Y"
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['check_in'] = date.strftime(date_format)

        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['check_out'] = result.strftime(date_format)

        check_in = datetime.datetime.strptime(data['check_in'], date_format)
        check_out = datetime.datetime.strptime(data['check_out'], date_format)
        days_in_hotel = (check_out - check_in).days

        bot.set_state(call.from_user.id, days_in_hotel, call.message.chat.id)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['days_in_hotel'] = days_in_hotel

        if data['photo']:
            photo = 'Да, загружать'
        else:
            photo = 'Нет, не нужно'

        if command == 'bestdeal':
            bot.send_message(call.from_user.id, f"Спасибо, проверьте ваши данные:\n"
                                                f"\nГород: {data['city'].title()}\n"
                                                f"Количество отелей для просмотра: {data['hotel_qty']}\n"
                                                f"Дата заселения: {data['check_in']}\n"
                                                f"Дата выезда: {data['check_out']}\n"
                                                f"Фото отелей: {photo}\n"
                                                f"Всего дней проживания: {data['days_in_hotel']}\n"
                                                f"Стоимость за ночь = от {data['min_price']} до {data['max_price']} долларов США\n"
                                                f"Расстояние от центра = от {data['min_distance']} до {data['max_distance']} км\n"
                                                f"\nЕсли всё верно - нажмите клавишу Да", reply_markup=answ.request_yes_no())

        else:
            bot.send_message(call.from_user.id, f"Спасибо, проверьте ваши данные:\n"
                                                f"\nГород: {data['city'].title()}\n"
                                                f"Количество отелей для просмотра: {data['hotel_qty']}\n"
                                                f"Дата заселения: {data['check_in']}\n"
                                                f"Дата выезда: {data['check_out']}\n"
                                                f"Фото отелей: {photo}\n"
                                                f"Всего дней проживания: {data['days_in_hotel']}\n"
                                                f"\nЕсли всё верно - нажмите клавишу Да", reply_markup=answ.request_yes_no())

        bot.set_state(call.from_user.id, UserAnswers.final, call.message.chat.id)

@bot.message_handler(state=UserAnswers.final)
def get_hotels(m: Message):
    """отправка запроса к API по ID города.
    Парсинг ответа, получение ID отелей и других данных.
     При необходимости снова запрос для получения фото и адреса.
     Запись данных о пользователе и отелях в БД"""

    with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
        command = data['command']
    if command == 'bestdeal':
        with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
            min_distanse = data['min_distance']
            max_distance = data['max_distance']

    if m.text.lower() == "да":
        bot.send_message(m.from_user.id, text='Ищу варианты по вашему запросу, нужно несколько секунд...')
        with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
            cust_data = data
        hotels_list = get_hotel_list(cust_data=cust_data)
        # print(hotels_list)
        hotels_qty = int(data['hotel_qty'])
        hotel_days = int(data['days_in_hotel'])
        city_name = data['city']
        count = 0
        try:
            for hotel in range(hotels_qty):
                hotel_id = int(hotels_list['data']['propertySearch']['properties'][hotel]['id'])
                hotel_name = hotels_list['data']['propertySearch']['properties'][hotel]['name']
                hotel_price = round(float(hotels_list['data']['propertySearch']['properties'][hotel]['price']['lead']['amount'],), 2)
                common_price = round(float(hotel_price * hotel_days), 2)
                hotel_location = hotels_list['data']['propertySearch']['properties'][hotel]['destinationInfo']['distanceFromDestination']['value']
                hotel_details = get_hotel_details(hotel_id=hotel_id)
                hotel_address = hotel_details['data']['propertyInfo']['summary']['location']['address']['addressLine']
                hotel_data = {          # делаю словарь с данными об отеле для сохранения в БД, фото не сохраняю.
                    'chat_id': m.chat.id,
                    'city_name': city_name,
                    'hotel_id': hotel_id,
                    'hotel_name': hotel_name,
                    'hotel_price': hotel_price,
                    'common_price': common_price,
                    'hotel_address': hotel_address,
                    'hotel_days': hotel_days,
                    'hotel_location': hotel_location

                }
                # add_response_to_db(hotel_data=hotel_data)

                if command == 'bestdeal':
                    if min_distanse < hotel_location < max_distance:
                        add_response_to_db(hotel_data=hotel_data)
                        count += 1
                        bot.send_message(m.from_user.id, text=
                                         f"Данные по отелю {hotel_name}: "
                                         f"\nАдрес: {hotel_address}"
                                         f"\nРасстояние от центра города = {hotel_location} км"
                                         f"\nСтоимость за 1 ночь = {hotel_price} долларов США"
                                         f"\nОбщая стоимость за {hotel_days} дней = {common_price} долларов США")
                        if data['photo']:
                            bot.send_message(m.from_user.id, text='Фотографии отеля:')
                            hotel_photos = data['photo_qty']
                            for photo in range(hotel_photos):
                                photo_url = hotel_details['data']['propertyInfo']['propertyGallery']['images'][photo]['image']['url']
                                description = hotel_details['data']['propertyInfo']['propertyGallery']['images'][photo]['image']['description']
                                bot.send_message(m.from_user.id, text=
                                f"{description}\n"
                                f"{photo_url}")



                else:
                    add_response_to_db(hotel_data=hotel_data)
                    bot.send_message(m.from_user.id, text=
                                     f"Данные по отелю {hotel_name}: "
                                     f"\nАдрес: {hotel_address}"
                                     f"\nРасстояние от центра города = {hotel_location} км"
                                     f"\nСтоимость за 1 ночь = {hotel_price} долларов США"
                                     f"\nОбщая стоимость за {hotel_days} дней = {common_price} долларов США")
                    if data['photo']:
                        bot.send_message(m.from_user.id, text='Фотографии отеля:')
                        hotel_photos = data['photo_qty']
                        for photo in range(hotel_photos):
                            photo_url = hotel_details['data']['propertyInfo']['propertyGallery']['images'][photo]['image']['url']
                            description = hotel_details['data']['propertyInfo']['propertyGallery']['images'][photo]['image']['description']
                            bot.send_message(m.from_user.id, text=
                            f"{description}\n"
                            f"{photo_url}")

            if command == 'bestdeal':
                if count == 0:
                    bot.send_message(m.from_user.id, text='К сожалению, отеля с вашими требованиями не найдено.'
                                                              'Попробуйте изменить запрос'
                                     )
                else:
                    bot.send_message(m.from_user.id, text='Это все найденные варианты, которые подходят под ваши требования.')
        except Exception as e:
            print('Exception risen', e)
            bot.send_message(m.from_user.id, text='Ошибка запроса к сайту отелей. Повторите запрос.')

        bot_help(m)
    elif m.text == '/history':
        history.get_history(m=m)

    else:
        bot.reply_to(m, "Попробуйте начать сначала, для ввода данных")
        bot_help(m)
