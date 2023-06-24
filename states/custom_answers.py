from telebot.handler_backends import State, StatesGroup



class UserAnswers(StatesGroup):
    command = State()
    chat_id = State()
    tgram_id = State()
    date_time = State()
    city = State()
    hotel_qty = State()
    date = State()
    photo = State()
    photo_qty = State()
    photo_qty_2 = State()
    city_id = State()
    check_in = State()
    check_out = State()
    final = State()
    days_in_hotel = State()

