from aiogram.fsm.state import State,StatesGroup

class StateFmsEditData(StatesGroup):
    choose_construction_object = State()
    choose_action = State()
    choose_floor_object = State()
    choose_room_object = State()
    edit_room_object = State()
    choose_action_data_room = State()

    edit_extra_wall_area = State()
    edit_plaster_type = State()
    edit_linear_meters = State()
    edit_walls_perimeter = State()
    edit_walls_height = State()
    edit_window_width = State()
    edit_window_height = State()
    edit_window_plaster_slopes = State()
    edit_window_plaster_four_sides = State()
    edit_window_arch_shape = State()
    edit_window_plaster_two_sides = State()