from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config.logging_admin import loger

from app.database.repository import db

from app.edit_data.keyboards import *
from app.start.keyboards import *
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



@router.message(F.text == "Вернуться на главную",StateFmsEditData.choose_action)
async def back(message: Message,state:FSMContext):
    await message.answer("Бот создан для расчета площади и строительного материала"
                         "Вы можете либо просмотреть, изменить данные в существующем объекте"
                         "либо создать новый проект",reply_markup=start_keyboard)
    await state.clear()


@router.message(F.text == "Вернуться на выбор объекта",StateFmsEditData.choose_floor_object)
async def back(message: Message,state:FSMContext):
    # Получаем список объектов
    construction_object_list = await db.get_construction_object(int(message.from_user.id))

    await state.update_data(construction_object_list=construction_object_list)

    text = "Ваши объекты:\n"
    count = 0
    for construction_object in construction_object_list:
        count += 1
        text += f"- №{count}: {construction_object.address}\n"
    await message.answer(text, reply_markup=choose_construction_object(count))

    await state.set_state(StateFmsEditData.choose_action)



@router.message(F.text == "Вернуться на отчет", StateFmsEditData.choose_action)
async def back(message: Message, state: FSMContext):
    data = await state.get_data()
    # Сохраняем объект
    construction_object = list(data.get("construction_object_list"))[int(message.text) - 1]
    await state.update_data(construction_object=construction_object)
    # Получаем данные и отчет
    list_data_report = await construction_object.generate_report()
    await message.answer(list_data_report[0])
    await message.answer(list_data_report[1], reply_markup=edit_construction_object)
    await state.set_state(StateFmsEditData.choose_floor_object)


@router.message(F.text == "Вернуться на отчет", StateFmsEditData.choose_room_object)
async def back(message: Message, state: FSMContext):
    data = await state.get_data()
    # Сохраняем объект
    construction_object = data.get("construction_object")
    await state.update_data(construction_object=construction_object)
    # Получаем данные и отчет
    list_data_report = await construction_object.generate_report()
    await message.answer(list_data_report[0])
    await message.answer(list_data_report[1], reply_markup=edit_construction_object)
    await state.set_state(StateFmsEditData.choose_floor_object)


@router.message(F.text == "Вернуться на выбор этажа", StateFmsEditData.edit_room_object)
async def back(message: Message, state: FSMContext):
    data = await state.get_data()
    # получаем все этажи
    floor_list = await db.get_floors(data.get("construction_object"))

    await state.update_data(floor_list=floor_list)
    text = "Выберите один из этажей\n"
    for intdex_floor, floor in enumerate(floor_list, start=1):
        text += f"- Этаж №{intdex_floor}\n"
    await message.answer(text, reply_markup=choose_floor(len(floor_list)))
    await state.set_state(StateFmsEditData.choose_room_object)


@router.message(F.text == "Вернуться на выбор комнаты", StateFmsEditData.choose_action_data_room)
async def back(message: Message, state: FSMContext):
    data = await state.get_data()
    floor = data.get("floor")
    room_list = await floor.rooms.all().order_by("id")
    await state.update_data(room_list=room_list, floor=floor)

    text = "Выберите нужную комнату\n"
    for intdex_room, room in enumerate(room_list, start=1):
        text += f"- Комната №{intdex_room}\n"
    await message.answer(text, reply_markup=choose_room(len(room_list)))
    await state.set_state(StateFmsEditData.edit_room_object)