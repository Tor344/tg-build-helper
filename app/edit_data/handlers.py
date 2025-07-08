from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
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
    await state.set_state(StateFmsEditData.choose_action)

#Получаем объект
@router.message(StateFmsEditData.choose_action)
async def edit_data(message: Message,state:FSMContext):
    data = await state.get_data()
    #Сохраняем объект
    construction_object = list(data.get("construction_object_list"))[int(message.text) - 1]
    await state.update_data(construction_object=construction_object)
   #Получаем данные и отчет
    list_data_report = await construction_object.generate_report()
    await message.answer(list_data_report[0])
    await message.answer(list_data_report[1], reply_markup=edit_construction_object)
    await state.set_state(StateFmsEditData.choose_floor_object)


# Входим в состояние редактирования данных
@router.message(F.text == "Редактировать данные", StateFmsEditData.choose_floor_object)
async def edit_data(message: Message, state: FSMContext):
    data = await state.get_data()
    #получаем все этажи
    floor_list = await db.get_floors(data.get("construction_object"))

    await state.update_data(floor_list=floor_list)
    text = "Выберите один из этажей\n"
    for intdex_floor, floor in enumerate(floor_list,start=1):
        text += f"- Этаж №{intdex_floor}\n"
    await message.answer(text, reply_markup=choose_floor(len(floor_list)))
    await state.set_state(StateFmsEditData.choose_room_object)


#Получаем этаж
@router.message(StateFmsEditData.choose_room_object)
async def edit_data(message: Message, state: FSMContext):
    try:
        numeral_floor = int(message.text)
        data = await state.get_data()
        floor = data.get("floor_list")[numeral_floor - 1]
        room_list = await floor.rooms.all().order_by("id")
        await state.update_data(room_list=room_list,floor=floor)

        text = "Выберите нужную комнату\n"
        for intdex_room, room in enumerate(room_list, start=1):
            text += f"- Комната №{intdex_room}\n"
        await message.answer(text, reply_markup=choose_room(len(room_list)))
        await state.set_state(StateFmsEditData.edit_room_object)
    except Exception as e:
        await message.answer("Сообщение должно быть числом")


#Получаем комнату
@router.message(StateFmsEditData.edit_room_object)
async def edit_data(message: Message, state: FSMContext):
    try:
        numeral_room = int(message.text)
        data = await state.get_data()

        #Сохраняем комнату
        room = data.get("room_list")[numeral_room - 1]
        await state.update_data(room=room)

        #Выводим все данные с инлайн кнопкой для изменения
        str_room, data_list_walls,data_list_windows = await room.get_data()
        await message.answer(str_room,reply_markup=room_edit_data)

        for index_walls, walls in enumerate(data_list_walls,start=0):
            await message.answer(walls,reply_markup=walls_edit_data(index_walls))

        for index_window, windows in enumerate(data_list_windows,start=0):
            await message.answer(windows,reply_markup=window_edit_data(index_window))
        await message.answer("Что вы хотите изменить?",reply_markup=beck_at_room)

        await state.set_state(StateFmsEditData.choose_action_data_room)
    except Exception as e:
        await message.answer("Сообщение должно быть числом")


@router.callback_query(StateFmsEditData.choose_action_data_room)
async def edit_data(call: CallbackQuery, state: FSMContext):
    datae = await state.get_data()
    room = datae.get("room")
    await call.answer("")

    if call.data == "edit_extra_wall_area":
        await call.message.answer("Введите Добавить доп. площадь стен:",reply_markup=remove_keyboard)
        await state.set_state(StateFmsEditData.edit_extra_wall_area)
    elif call.data == "edit_plaster_type":
        room.plaster_type = "Цементная" if room.plaster_type == "Гипсовая" else "Гипсовая"
        room.seve()
        await call.message.answer(f"Тип штукатурки изменен на {"Цементная" if not(room.plaster_type) == "Гипсовая" else "Гипсовая"}")
    elif call.data == "edit_linear_meters":
        await call.message.answer("Введите погонные метры:")
        await state.set_state(StateFmsEditData.edit_linear_meters)

    await state.update_data(index=int(call.data.split("_")[-1]))

    if  call.data.startswith("edit_walls_perimeter_"):

        await call.message.answer("Введите периметр стен:",reply_markup=remove_keyboard)
        await state.set_state(StateFmsEditData.edit_walls_perimeter)

    elif call.data.startswith("edit_walls_height_"):
        await call.message.answer("Введите высоту стен:", reply_markup=remove_keyboard)
        await state.set_state(StateFmsEditData.edit_walls_height)

    windows = await room.windows.all().order_by("id")

    if call.data.startswith("edit_window_width_"):
        await call.message.answer("Введите ширину окна:", reply_markup=remove_keyboard)
        await state.set_state(StateFmsEditData.edit_window_width)

    elif call.data.startswith("edit_window_height_"):
        await call.message.answer("Введите высоту стен:", reply_markup=remove_keyboard)
        await state.set_state(StateFmsEditData.edit_window_height)


    elif call.data.startswith("edit_window_plaster_slopes_"):
        index = int(call.data.split("_")[-1])
        windows[index].needs_plaster = not(windows[index].needs_plaster)
        await windows[index].save()
        await call.message.answer(f"Теперь штукатурка откосов {"не" if not(windows[index].needs_plaster) else ""} нужна",reply_markup=beck_at_room)

    elif call.data.startswith("edit_window_plaster_four_sides_"):
        index = int(call.data.split("_")[-1])
        windows[index].plaster_all_sides = not (windows[index].plaster_all_sides)
        await windows[index].save()
        await call.message.answer(
            f"Теперь штукатурка откосов с 4 сторон {"не" if not (windows[index].plaster_all_sides) else ""} нужна",reply_markup=beck_at_room)

    elif call.data.startswith("edit_window_arch_shape_"):
        index = int(call.data.split("_")[-1])
        windows[index].is_arched = not (windows[index].is_arched)
        await windows[index].save()
        await call.message.answer(
            f"Теперь окно {"не" if not (windows[index].is_arched) else ""} арочное",reply_markup=beck_at_room)

    elif call.data.startswith("edit_window_plaster_two_sides_"):
        index = int(call.data.split("_")[-1])
        windows[index].plaster_two_sides = not (windows[index].plaster_two_sides)
        await windows[index].save()
        await call.message.answer(
            f"Теперь штукатурка откосов с 2 сторон {"не" if not (windows[index].plaster_two_sides) else ""} нужна",reply_markup=beck_at_room)



@router.message(StateFmsEditData.edit_extra_wall_area)
async def edit_data(message: Message, state:FSMContext):
    data = await state.get_data()
    room = data.get("room")
    room.extra_wall_area = message.text
    await room.save()
    await message.answer("Данные изменены",reply_markup=beck_at_room)
    await state.set_state(StateFmsEditData.choose_action_data_room)


@router.message(StateFmsEditData.edit_linear_meters)
async def edit_data(message: Message, state:FSMContext):
    data = await state.get_data()
    room = data.get("room")
    room.linear_meters = message.text
    await room.save()
    await message.answer("Данные изменены",reply_markup=beck_at_room)
    await state.set_state(StateFmsEditData.choose_action_data_room)


@router.message(StateFmsEditData.edit_walls_perimeter)
async def edit_data(message: Message, state:FSMContext):
    data = await state.get_data()
    room = data.get("room")
    index = int(data.get("index"))
    walls = await room.walls.all().order_by("id")
    walls[index].perimeter = message.text
    await walls[index].save()
    await message.answer("Данные изменены",reply_markup=beck_at_room)
    await state.set_state(StateFmsEditData.choose_action_data_room)


@router.message(StateFmsEditData.edit_walls_height)
async def edit_data(message: Message, state:FSMContext):
    data = await state.get_data()
    room = data.get("room")
    index = int(data.get("index"))
    walls = await room.walls.all().order_by("id")
    walls[index].height = message.text
    await walls[index].save()
    await message.answer("Данные изменены",reply_markup=beck_at_room)
    await state.set_state(StateFmsEditData.choose_action_data_room)


@router.message(StateFmsEditData.edit_window_height)
async def edit_data(message: Message, state:FSMContext):
    data = await state.get_data()
    room = data.get("room")
    index = int(data.get("index"))
    windows = await room.windows.all().order_by("id")
    windows[index].height = message.text
    await windows[index].save()
    await message.answer("Данные изменены",reply_markup=beck_at_room)
    await state.set_state(StateFmsEditData.choose_action_data_room)


@router.message(StateFmsEditData.edit_window_width)
async def edit_data(message: Message, state:FSMContext):
    data = await state.get_data()
    room = data.get("room")
    index = int(data.get("index"))
    windows = await room.windows.all().order_by("id")
    windows[index].width = message.text
    await windows[index].save()
    await message.answer("Данные изменены",reply_markup=beck_at_room)
    await state.set_state(StateFmsEditData.choose_action_data_room)

































