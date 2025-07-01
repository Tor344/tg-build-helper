from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton,ReplyKeyboardRemove

start_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="start",callback_data='start_inline_keyboard')]])




def get_inline_keyboard(states:dict) -> InlineKeyboardMarkup:


    buttons = [
        [InlineKeyboardButton(
            text=f" {'✔️' if states[0] else ''} Нужна ли штукатурка откосов",
            callback_data="toggle_0"
        )],
        [InlineKeyboardButton(
            text=f"{'✔️' if states[1] else ''} Штукатурка с 4 сторон ",
            callback_data="toggle_1"
        )],
        [InlineKeyboardButton(
            text=f"{'✔️' if states[2] else ''} Окно арочной формы ",
            callback_data="toggle_2"
        )],
        [InlineKeyboardButton(
            text=f"{'✔️' if states[3] else ''} Штукатурка только с 2 сторон ",
            callback_data="toggle_3"
        )],
        [InlineKeyboardButton(
            text="Продолжить",
            callback_data="continue"
        )],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)


    return keyboard


remove_keyboard = ReplyKeyboardRemove()

start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[[KeyboardButton(text="Существующие объекты")],
                                                                    [KeyboardButton(text="Создать объект")]])

def choosing_floor(count: list) -> ReplyKeyboardMarkup:
    """Требует int количество этажей"""
    keyboard_buttons = []
    for item in reversed(count):
        keyboard_buttons.append([KeyboardButton(text=str(item))])
    return ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True,
    )

type_plaster = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[[KeyboardButton(text="Цементная")],
                                                                  [KeyboardButton(text="Гипсовая")]])

finish_walls = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[[KeyboardButton(text="Добавить стены с другой высотой")],
                                                                  [KeyboardButton(text="Продолжить")]]
                                   )

finish_window = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[[KeyboardButton(text="Добавить окно")],
                                                                   [KeyboardButton(text="Продолжить")]])

finish_floor = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[[KeyboardButton(text="Добавить среднюю толщину штукатурки, коментарии к объекту и закончить")],
                                                                  [KeyboardButton(text="Заполнить другой этаж")]])