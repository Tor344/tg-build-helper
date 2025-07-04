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
@router.message(F.text == "Существующие объекты")
async def edit_data(message: Message,state:FSMContext):

    #Получаем список объектов
    construction_object_list = await db.get_construction_object(int(message.from_user.id))

    await state.update_data(construction_object_list=construction_object_list)

    text = "Ваши объекты:\n"
    count = 0
    for construction_object in construction_object_list:
        count += 1
        text += f"- №{count}: {construction_object.address}\n"
    await message.answer(text, reply_markup=choose_construction_object(count))
    await state.set_state(StateFmsEditData.edit_construction_object)


@router.message(StateFmsEditData.edit_construction_object)
async def edit_data(message: Message,state:FSMContext):
    data = await state.get_data()
    construction_object = list(data.get("construction_object_list"))[int(message.text) - 1]
    await state.update_data(construction_object=construction_object)
    text = await db.generate_construction_object_report(construction_object)
    await message.answer(text, reply_markup=edit_construction_object)

