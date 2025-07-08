from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config.logging_admin import loger

from app.database.repository import db

from app.edit_data.keyboards import *
from app.edit_data.state_fms import StateFmsEditData

router = Router()

#Выводим объекты
@router.message(F.text == "Удалить объект",StateFmsEditData.choose_action)
async def edit_data_delite(message: Message,state:FSMContext):
    data = await state.get_data()
    construction_object = data.get("construction_object")
    await db.delete_construction_object(construction_object)
    await state.update_data(construction_object=None)
    await message.answer(f"Объект удален")

    construction_object_list = await db.get_construction_object(int(message.from_user.id))

    await state.update_data(construction_object_list=construction_object_list)

    text = "Ваши объекты:\n"
    count = 0
    for construction_object in construction_object_list:
        count += 1
        text += f"- №{count}: {construction_object.address}\n"
    await message.answer(text, reply_markup=choose_construction_object(count))
    await state.set_state(StateFmsEditData.choose_construction_object)



