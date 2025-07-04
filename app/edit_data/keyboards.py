from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


start_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="start",callback_data='start_inline_keyboard')]])

start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[[KeyboardButton(text="Существующие объекты")],
                                                                    [KeyboardButton(text="Создать объект")]])

remove_keyboard = ReplyKeyboardRemove()

def choose_construction_object(count:int):
    keyboard_buttons = []
    for _ in range(1,count + 1):
        keyboard_buttons.append([KeyboardButton(text=str(_))])
    keyboard_buttons.append([KeyboardButton(text="Вернуться на главную")])
    return ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True,
    )



edit_construction_object = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[[KeyboardButton(text="Редактировать данные"),
                                                                              KeyboardButton(text="Удалить объект")],
                                                                            [KeyboardButton(text="Вернуться назад")]])