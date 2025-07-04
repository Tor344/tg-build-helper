from aiogram.fsm.state import State,StatesGroup

class StateFmsEditData(StatesGroup):
    choose_construction_object = State()
    edit_construction_object = State()