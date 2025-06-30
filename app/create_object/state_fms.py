from aiogram.fsm.state import State,StatesGroup

class InputData(StatesGroup):
    name_object = State()
    count_floor = State()
    start_floor = State()

    # Данные стен
    walls_perimeter = State()  # Периметр стен
    walls_height = State()  # Высота потолков
    finish_walls = State()
    input_status_walls = State()
    # Дополнительная площадь стен
    extra_wall_area = State()  # Добавить доп. площадь стен
    plaster_type = State()  # Тип штукатурки (цементная/гипсовая)
    linear_meters = State()  # Погонные метры

    # Данные окон
    window_width = State()  # Ширина окна
    window_height = State()  # Высота окна
    window_data = State()
    # window_plaster_slopes = State()  # Нужна ли штукатурка откосов
    # window_plaster_four_sides = State()  # Штукатурка с 4 сторон
    # window_arch_shape = State()  # Окно арочной формы
    # window_plaster_two_sides = State()  # Штукатурка только с 2 сторон
    finish_window = State()
    # Дверной проем
    door_area = State()  # Площадь дверного проема

    # Завершение замера
    finish_measurement = State()  # Состояние перед завершением
    plaster_thickness = State()  # Средняя толщина слоя штукатурки