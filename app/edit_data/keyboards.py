from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


start_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="start",callback_data='start_inline_keyboard')]])

start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,keyboard=[[KeyboardButton(text="Существующие объекты")],
                                                                    [KeyboardButton(text="Создать объект")]])

remove_keyboard = ReplyKeyboardRemove()


room_edit_data = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Изменить Доп. площадь",callback_data='edit_extra_wall_area')],
                                                       [InlineKeyboardButton(text="Изменить тип штукатурки",callback_data='edit_plaster_type')],
                                                       [InlineKeyboardButton(text="Изменить погонные метры",callback_data='edit_linear_meters')],])

def walls_edit_data(count:int):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Изменить периметр стен",callback_data=f'edit_walls_perimeter_{count}')],
                                                       [InlineKeyboardButton(text="Изменить высоту стен",callback_data=f'edit_walls_height_{count}')]])


def window_edit_data(count:int):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Изменить ширину окна",callback_data=f'edit_window_width_{count}')],
                                                       [InlineKeyboardButton(text="Изменить высоту окна",callback_data=f'edit_window_height_{count}')],
                                                 [InlineKeyboardButton(text="Изменить нужна ли штукатурка откосов",callback_data=f'edit_window_plaster_slopes_{count}')],
                                                 [InlineKeyboardButton(text="Изменить оштукатурить все 4 стороны",callback_data=f'edit_window_plaster_four_sides_{count}')],
                                                 [InlineKeyboardButton(text="Изменить арочное окно",callback_data=f'edit_window_arch_shape_{count}')],
                                                 [InlineKeyboardButton(text="Изменить только 2 стороны",callback_data=f'edit_window_plaster_two_sides_{count}')]])





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

def edit_room_object():
    pass
