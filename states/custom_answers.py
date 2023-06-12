from telebot.handler_backends import State, StatesGroup



class UserAnswers(StatesGroup):
    city = State()
    hotel_qty = State()
    date = State()
    photo = State()
    photo_qty = State()
    photo_qty_2 = State()
    city_id = State()
    check_in = State()
    check_out = State()
