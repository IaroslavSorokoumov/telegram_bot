from telebot.types import Message
import requests
from telebot import types
from loader import bot
from states.custom_answers import UserAnswers
import json

def api_request(method_endswith, params, method_type):
    """
    функция для запроса к API
    :param method_endswith: конкретный запрос к API
    :param params: параметры запроса - ключи и значения
    :param method_type: метод get или post
    :return: функцию запроса к API - GET/POST
    """
    url = f"https://hotels4.p.rapidapi.com/{method_endswith}"

    # В зависимости от типа запроса вызываем соответствующую функцию
    if method_type == 'GET':
        return get_request(
            url=url,
            params=params
        )
    else:
        return post_request(
            url=url,
            params=params
        )


def get_request(url, params):
    """запрос к API для извлечения данных по указанному URL и с нужными параметрами"""
    try:
        response = requests.get(
            url,
            params=params,
            headers={
                "X-RapidAPI-Key": "ec16790110msh47fb999be2bc46ap174b48jsn861c60ef2748",
                "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
            },
            timeout=10
        )
        if response.status_code == requests.codes.ok:
            return response.json()
    except requests.exceptions.Timeout:
        return f"Нет ответ от сервера. Попробуйте повторить запрос"
    except requests.exceptions.RequestException:
        return f"Ошибка запроса. Необходимо повторить запрос"

def post_request(url, params):
    """запрос к API с отправкой данных по указанному URL и с нужными параметрами
    получение данных с сервера"""
    try:
        response = requests.post(
            url,
            params=params,
            headers={
                "content-type": "application/json",
                "X-RapidAPI-Key": "ec16790110msh47fb999be2bc46ap174b48jsn861c60ef2748",
                "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
            },
            timeout=10
        )
    except requests.exceptions.Timeout:
        return f"Нет ответ от сервера. Попробуйте повторить запрос"
    except requests.exceptions.RequestException:
        return f"Ошибка запроса. Необходимо повторить запрос"


@bot.message_handler(commands=["lowprice"])
def lowprice(m: Message) -> None:
    """функция обработки запроса /lowprice. Ловим ответ пользователя - город для поиска отеля"""
    bot.set_state(m.from_user.id, UserAnswers.city, m.chat.id)
    bot.send_message(m.from_user.id, text='Какой город вас интересует? ')


@bot.message_handler(state=UserAnswers.city)
def get_city_name(m: Message) -> None:
    """Записываем название города в состояние пользователя и задаём вопрос по кол-ву отелей"""

    if m.text.isalpha():
        bot.reply_to(m, 'Отлично. Cколько отелей хотите просмотреть (не более 5)?')
        bot.set_state(m.from_user.id, UserAnswers.hotel_qty, m.chat.id)

        with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
            data['city'] = m.text
    else:
        bot.reply_to(m, "Ошибка в написании города. Должны быть только буквы")


@bot.message_handler(state=UserAnswers.hotel_qty)
def get_hotel_qty(m: Message) -> None:
    """Записываем кол-во отелей в состояние пользователя и спрашиваем про фото отелей"""

    if m.text.isdigit() and 0 < int(m.text) < 6:
        bot.reply_to(m, 'Принято. Нужно ли подгрузить фото отелей (Да/Нет)?')
        bot.set_state(m.from_user.id, UserAnswers.photo, m.chat.id)

        with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
            data['hotel_qty'] = m.text
    else:
        bot.reply_to(m, "Ошибка. Только цифры и не более 5")


@bot.message_handler(state=UserAnswers.photo)
def get_photo(m: Message) -> None:
    """Записываем кол-во отелей в состояние пользователя и задаём след. вопрос"""

    if m.text.lower() == 'да':
        bot.reply_to(m, 'Спасибо. Сколько фото показать (не более 3-х)?')
        bot.set_state(m.from_user.id, UserAnswers.photo_qty, m.chat.id)

        with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
            data['photo'] = m.text
    elif m.text.lower() == 'нет':
        bot.set_state(m.from_user.id, UserAnswers.photo_qty, m.chat.id)
        bot.reply_to(m, 'Спасибо.')

        with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
            data['photo'] = m.text
    else:
        bot.reply_to(m, "Ошибка. Только ответ Да или Нет")


@bot.message_handler(state=UserAnswers.photo_qty)
def get_photo_qty(m: Message) -> None:
    if m.text.isdigit() and 0 < int(m.text) < 4:
        bot.reply_to(m, 'Спасибо. Записал. Выполняю поиск.')

        with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
            data['photo_qty'] = m.text
    elif UserAnswers.photo_qty == 0:
        with bot.retrieve_data(m.from_user.id, m.chat.id) as data:
            data['photo_qty'] = "0"

    else:
        bot.reply_to(m, 'Ошибка в количестве фото, не менее 1 и не более 3-х')
    text = f"Ваш город - {data['city']}\n" \
           f"Количество отелей для поиска - {data['hotel_qty']}\n" \
           f"Количество необходимых фотографий - {data['photo_qty']}"
    bot.send_message(m.from_user.id, text)






# @bot.message_handler(content_types='text')
# def get_city_id(m: Message):
#     response = api_request(get_id_url, {"q": m.text, "locale": "ru_RU"}, 'GET')
#     city_id = response['sr'][0]['gaiaId']
#     bot.send_message(m.chat.id, f"ID отеля = {city_id}")
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     btn1 = types.KeyboardButton("Да")
#     btn2 = types.KeyboardButton("Нет")
#     markup.add(btn1, btn2)
#     hotel_photo = bot.reply_to(m, text="Нужно ли загружать фото? ", reply_markup=markup)
#     bot.register_next_step_handler(city_id, hotel_photo, get_hotel_info)
#
# @bot.message_handler()
# def get_hotel_info(m: Message):
#     response = api_request(
#         req_hotel_prop,
#         {'currency': 'USD',
#          'eapid': 1,
#          'locale': 'ru_RU',
#          'siteId': 300000001,
#          'destination': {
#              'regionId': int(m.text)
#          },
#          'checkInDate': {'day': 7, 'month': 12, 'year': 2023},
#          'checkOutDate': {'day': 9, 'month': 12, 'year': 2023},
#          'rooms': [{'adults': 1}],
#          'resultsStartingIndex': 0,
#          'resultsSize': 10,
#          'sort': 'PRICE_LOW_TO_HIGH',
#          'filters': {'availableFilter': 'SHOW_AVAILABLE_ONLY'}
#          }
#
#     )



# @bot.message_handler(content_types='text')
# def city_step(m: Message):
#     """функция для принятия ответа от пользователя: название отеля, кол-во отелей для просмотра
#     Ответ по клавишам или текстом"""
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     btn1 = types.KeyboardButton("1")
#     btn2 = types.KeyboardButton("2")
#     btn3 = types.KeyboardButton("3")
#     btn4 = types.KeyboardButton("4")
#     btn5 = types.KeyboardButton("5")
#     markup.add(btn1, btn2, btn3, btn4, btn5)
#     if m.text.isalpha():
#         userCity = m.text
#         msgHotels = bot.reply_to(m, text="Сколько отелей вы хотите просмотреть? "
#                                          "Укажите цифру нажав клавишу (не более 5).",
#                                  reply_markup=markup)
#         bot.register_next_step_handler(msgHotels, hotels_step)
#         return userCity
#     else:
#         markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         btn1 = types.KeyboardButton("/help")
#         btn2 = types.KeyboardButton("/lowprice")
#         markup.add(btn1, btn2)
#         bot.reply_to(m, "Ошибка при вводе города. Нажмите клавишу для нового запроса", reply_markup=markup)

#
# @bot.message_handler(content_types='text')
# def hotels_step(m: Message) -> int:
#     """Получаем ответ по кол-ву отелей и запоминаем.
#     Задаём вопрос о получении фото отеля, да или нет.
#     ответ по клавишам"""
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     btn1 = types.KeyboardButton("Да")
#     btn2 = types.KeyboardButton("Нет")
#     markup.add(btn1, btn2)
#     if m.text.isdigit() and 0 < int(m.text) < 4:
#         hotelsQty = int(m.text)
#         msgPhoto = bot.send_message(m.chat.id, text="Нужны ли фото отеля? Да/Нет.", reply_markup=markup)
#         bot.register_next_step_handler(msgPhoto, photo_step)
#         return hotelsQty
#     else:
#         bot.reply_to(m, "Ошибка в кол-ве отелей.")
#
#
# @bot.message_handler(content_types='text')
# def photo_step(m: Message) -> int:
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     btn1 = types.KeyboardButton("1")
#     btn2 = types.KeyboardButton("2")
#     btn3 = types.KeyboardButton("3")
#     markup.add(btn1, btn2, btn3)
#     if m.text.lower() == "да":
#         photoQty = bot.send_message(m.chat.id, text="Укажите кол-во фото. Не более 3-х", reply_markup=markup)
#         # bot.register_next_step_handler(photoQty, hotel_info)
#         return photoQty
#     else:
#         bot.reply_to(m, 'Информация об отеле будет выдана без фото"')
#
# def hotel_info():
#     city = city_step
#     url = "https://hotels4.p.rapidapi.com/locations/v3/search"
#     querystring = {"q": city, "locale": "ru_RU", "langid": "1033", "siteid": "300000001"}
#     headers = {
#         "X-RapidAPI-Key": "ec16790110msh47fb999be2bc46ap174b48jsn861c60ef2748",
#         "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
#     }
#     response = requests.get(url, headers=headers, params=querystring)
#     print(response.json())
#


    # @bot.message_handler(commands=['addproduct'])
    # def handle_text(message):
    #     cid = message.chat.id
    #     msgPrice = bot.send_message(cid, 'Set your price:')
    #     bot.register_next_step_handler(msgPrice, step_Set_Price)
    #
    # def step_Set_Price(message):
    #     cid = message.chat.id
    #     userPrice = message.text





    # def get_hotel_info():
    #     url = "https://hotels4.p.rapidapi.com/properties/get-details"
    #
    #     querystring = {
    #         "id": "your_hotel_id"  # Замените "your_hotel_id" на фактический идентификатор отеля
    #     }
    #
    #     headers = {
    #         "X-RapidAPI-Key": "your_rapidapi_key"  # Замените "your_rapidapi_key" на ваш ключ RapidAPI
    #     }
    #
    #     response = requests.request("GET", url, headers=headers, params=querystring)
    #
    #     if response.status_code == 200:
    #         hotel_info = response.json()
    #         # Обработка полученных данных об отеле
    #         print(hotel_info)
    #     else:
    #         print("Ошибка при выполнении запроса:", response.status_code)
    #
    # get_hotel_info()
    #
# url = "https://hotels4.p.rapidapi.com/locations/search"
#
# querystring = {"query":"new york","locale":"en_US"}
#
# headers = {
# 	"X-RapidAPI-Key": "ec16790110msh47fb999be2bc46ap174b48jsn861c60ef2748",
# 	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
# }
#
# response = requests.get(url, headers=headers, params=querystring)
#
# print(response.json())


get_id_url = "locations/v3/search"
req_hotel_prop = "properties/v2/list"
req_hotel_prop_detailed = "properties/v2/detail"