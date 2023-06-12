from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, Dict
from loader import bot


def city_keybord(m: Message, city_dict: Dict):
    buttons = InlineKeyboardMarkup()
    for k, v in city_dict.items():
        buttons.add(InlineKeyboardButton(text=k, callback_data=str(v)))
    bot.send_message(m.from_user.id, "Уточните, пожалуйста, нажав нужную клавишу",
                     reply_markup=buttons)
    return buttons