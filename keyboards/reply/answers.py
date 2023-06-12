from telebot import types


def request_yes_no() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn1 = types.KeyboardButton("Да")
    btn2 = types.KeyboardButton("Нет")
    return markup.add(btn1, btn2)

def request_photo() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn1 = types.KeyboardButton('1')
    btn2 = types.KeyboardButton('2')
    btn3 = types.KeyboardButton('3')
    return markup.add(btn1, btn2, btn3)

def further() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text="Далее")
    return markup.add(btn1)

def request_hotels() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn1 = types.KeyboardButton('1')
    btn2 = types.KeyboardButton('2')
    btn3 = types.KeyboardButton('3')
    btn4 = types.KeyboardButton('4')
    btn5 = types.KeyboardButton('5')
    return markup.add(btn1, btn2, btn3, btn4, btn5)