from aiogram import Router, F
from aiogram.types import Message,CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config.logging_admin import loger

from app.database.repository import db

from app.create_object.keyboards import *
from app.create_object.state_fms import InputData

router = Router()


@router.message(F.text == "Создать объект")
async def create_object(message: Message,state: FSMContext):
    #пользователь
    await message.answer("Введите адрес объекта:",reply_markup=remove_keyboard)
    await state.set_state(InputData.name_object)


#получаем адрес и создаем новый объект
@router.message(InputData.name_object)
async def create_object(message: Message,state: FSMContext):
    #данные
    construction_object = await db.add_construction_object(user=int(message.from_user.id), address=message.text)
    await state.update_data(construction_object=construction_object)

    #пользователь
    await message.answer("Введите количество этажей:")
    await state.set_state(InputData.count_floor)


#получем количество этажей и создаем этажи
@router.message(InputData.count_floor)
async def create_object(message: Message,state: FSMContext):
    if not(message.text.isdigit()):
        await message.answer("Сообщение должно быть числом")
        return

    #данные
    await state.update_data(count_walls=0,count_room=0)
    data = await state.get_data()
    floors_list = []
    #создаем этажи и добавляем в список floors_list
    for _ in range(int(message.text)):  # создаём N этажей
        floor = await db.add_floor(data["construction_object"])  # добавляем этаж в БД
        floors_list.append(floor)  # сохраняем в список
    count_floor = [int(x) for x in range(1,int(message.text)+1)]
    await state.update_data(count_floor = count_floor,floors_list=floors_list)

    #пользователь
    await message.answer("Выберите этаж с которого хотите начать замер:",reply_markup=choosing_floor(count_floor))
    await state.set_state(InputData.start_floor)


#получем стартовый этаж и создаем комнату
@router.message(InputData.start_floor)
async def create_object(message: Message,state: FSMContext):
    if not(message.text.isdigit()):
        await message.answer("Сообщение должно быть числом")
        return
    #данные
    data = await state.get_data()
    #Создаем комнату
    room = await db.add_room(floor= data["floors_list"][int(message.text)-1])
    count_floor = list(data["count_floor"])
    count_floor.remove(int(message.text))

    await state.update_data(count_walls=int(data["count_walls"]) + 1,count_room=int(data["count_room"]) + 1,
                            count_floor=count_floor,number_floor=int(message.text),room = room)


    #пользователь

    await message.answer(f"Начинаем вносить данные этажа № {int(message.text)}\n"
                         f"Комнаты №{data["count_room"]+1}\n"
                         f"Стены с одной высотой № {data["count_walls"] +1}\n"
                        "Введите периметр стен в метрах:",reply_markup=remove_keyboard)

    await state.set_state(InputData.walls_perimeter)


#получем периметр стен
@router.message(InputData.walls_perimeter)
async def create_object(message: Message,state: FSMContext):
    try:
        perimeter = float(message.text)
        if perimeter < 0:
            await message.answer("Число должно быть больше или ровно 0")
            return
        #данные
        await state.update_data(walls_perimeter=perimeter)
        # пользователь

        await message.answer("Введите высоту стен в метрах:")
    except ValueError:
        await message.answer("Сообщение должно быть числом")
        return

    finally:
        if perimeter >= 0:
            await state.set_state(InputData.finish_walls)


#Получаем высоту стены
@router.message(InputData.finish_walls)
async def create_object(message: Message,state: FSMContext):
    try:
        height = float(message.text)
        if height < 0:
            await message.answer("Число должно быть больше или ровно 0")
            return

        #создаем стены
        data = await state.get_data()
        await db.add_wall(data["room"], float(data["walls_perimeter"]), height)

        await message.answer("Выберите один из вариантов",reply_markup=finish_walls)
    except ValueError:
        await message.answer("Сообщение должно быть числом")
        return

    finally:
        if height >= 0:
            await state.set_state(InputData.input_status_walls)


#продолжаем заполнять или возврашаем на запонение еще одной стены
@router.message(InputData.input_status_walls)
async def create_object(message: Message,state: FSMContext):
    if message.text == "Продолжить":
        await message.answer("Введите доп. площадь стен в метрах квадратных:",reply_markup=remove_keyboard)
        await state.set_state(InputData.extra_wall_area)
    elif message.text == "Добавить стены с другой высотой":
        data = await state.get_data()
        await state.update_data(count_walls=int(data["count_walls"]) + 1)
        await message.answer(f"Добавление данных стен с другой высотой №{data["count_walls"] +1}\n"
                             "Введите периметр стен в метрах:", reply_markup=remove_keyboard)
        await state.set_state(InputData.walls_perimeter)

    else:
        await message.answer("Выберите один из предложенных вариантов")


#получем доп. площадь стен
@router.message(InputData.extra_wall_area)
async def create_object(message: Message,state: FSMContext):
    try:
        extra_wall_area = float(message.text)
        if extra_wall_area < 0:
            await message.answer("Число должно быть больше или ровно 0")
            return
        await state.update_data(extra_wall_area=extra_wall_area)
        await message.answer("Выберите тип штукатурки:",reply_markup=type_plaster)

    except ValueError:
        await message.answer("Сообщение должно быть числом")
        return
    finally:
        if extra_wall_area >= 0:
            await state.set_state(InputData.plaster_type)


#Получаем тип штукатурки
@router.message(InputData.plaster_type)
async def create_object(message: Message,state: FSMContext):
    if message.text not in ['Цементная','Гипсовая']:
        await message.answer("Выберите один из предложенных вариантов:")
        return
    await state.update_data(count_window=0)
    await state.update_data(plaster_type=message.text)
    await message.answer("Введите количество погонных метров",reply_markup=remove_keyboard)
    await state.set_state(InputData.linear_meters)


#Получаем погонные метры
@router.message(InputData.linear_meters)
async def create_object(message: Message,state: FSMContext):
    try:
        linear_meters = float(message.text)
        if linear_meters < 0:
            await message.answer("Число должно быть больше или ровно 0")
            return
        await state.update_data(linear_meters=linear_meters)
        data = await state.get_data()
        await state.update_data(count_window=data["count_window"] + 1)
        await message.answer(f"Начинаем заполнять окна №{data["count_window"]+1}\n"
            "Введите ширину окна в метрах:")

    except ValueError:
        await message.answer("Сообщение должно быть числом")
        return

    finally:
        if linear_meters >= 0:
            await state.set_state(InputData.window_width)


#Получаем ширину окна
@router.message(InputData.window_width)
async def create_object(message: Message,state: FSMContext):
    try:
        window_width = float(message.text)
        if window_width < 0:
            await message.answer("Число должно быть больше или ровно 0")
            return
        await state.update_data(window_width=window_width)
        await message.answer("Введите высоту окна в метрах:")

    except ValueError:
        await message.answer("Сообщение должно быть числом")
        return

    finally:
        if window_width >= 0:
            await state.set_state(InputData.window_height)



#Получаем высоту окна
@router.message(InputData.window_height)
async def create_object(message: Message,state: FSMContext):
    try:
        window_height = float(message.text)
        if window_height < 0:
            await message.answer("Число должно быть больше или ровно 0")
            return
        await state.update_data(window_height=window_height)
        await state.update_data(window_data={0:False,1:False,2:False,3:False})

        await message.answer("Выберите нужные пункты",reply_markup=get_inline_keyboard({0:False,1:False,2:False,3:False}))

    except ValueError:
        await message.answer("Сообщение должно быть числом")
        return

    finally:
        if window_height >= 0:
            await state.set_state(InputData.window_data)


#получаем данные окна
@router.callback_query(InputData.window_data)
async def create_object(call:CallbackQuery,state: FSMContext):
    await call.answer("")

    data = await state.get_data()
    if call.data.startswith("toggle_"):
        # Получаем индекс из callback data
        index = int(call.data.split("_")[1])
        # Проверяем что индекс в пределах массива
        if 0 <= index < len(data["window_data"]):
            # Переключаем значение (True -> False, False -> True)
            data["window_data"][index] = not data["window_data"][index]
        await state.update_data(window_data=data["window_data"])
        await call.message.edit_text('Выберите нужные пункты',
                                     reply_markup=get_inline_keyboard(data["window_data"]))
        return

    await call.message.answer("Выберите один из вариантов",reply_markup=finish_window)
    await state.set_state(InputData.finish_window)


#переходим к получению площади дверного проема или добавляем еще одно окно
@router.message(InputData.finish_window)
async def create_object(message: Message,state: FSMContext):
    #создаем окно
    data = await state.get_data()
    window_db = await db.add_window(room=data["room"],width=data["window_width"],
                                    height=data["window_height"],data_window=list(data["window_data"]))
    if message.text == "Продолжить":
        await message.answer("Введите площадь дверного проема в метрах квадратных:",reply_markup=remove_keyboard)
        await state.set_state(InputData.door_area)
    elif message.text == "Добавить окно":
        await state.update_data(count_window=data["count_window"] + 1)
        await message.answer(f"Добавление еще одного окна №{data["count_window"] + 1}\n"
                             "Введите высоту окна в метрах:", reply_markup=remove_keyboard)
        await state.set_state(InputData.window_width)
    else:
        await message.answer("Выберите один из предложенных вариантов")


#получаем площадь дверного проема
@router.message(InputData.door_area)
async def create_object(message: Message,state: FSMContext):
    try:
        print(message.text)
        door_area = float(message.text)
        if door_area < 0:
            await message.answer("Число должно быть больше или ровно 0")
            return
        await state.update_data(door_area=door_area)
        await message.answer("Выберите один из вариантов:",reply_markup=finish_room)
    except ValueError:
        await message.answer("Сообщение должно быть числом")
        return
    finally:
        if door_area >= 0:
            await state.set_state(InputData.finish_room)


#добавляем комнату или переходим на другой этаж
@router.message(InputData.finish_room)
async def create_object(message: Message,state: FSMContext):
    try:
        data = await state.get_data()
        room = await db.append_room(room=data["room"], extra_wall_area=data['extra_wall_area'],
                                    plaster_type=data["plaster_type"], linear_meters=data["linear_meters"],
                                    door_area=data["door_area"])
        if message.text == "Добавить комнату":

            await state.update_data(count_window=0, count_walls=0)
            await message.answer(f"Начинаем вносить данные для этада № {data["number_floor"]}\n"
                         f"Для комнаты № {data["count_room"]}\n"
                         f"Стены с одной высотой № 1\n"
                        "Введите периметр стен в метрах:",reply_markup=remove_keyboard)

            await state.set_state(InputData.walls_perimeter)
            return
        elif message.text == "Перейти на другой этаж если таковые имеются":
            if data["count_floor"] == []:
                await message.answer("Введите среднюю толщину штукатурки в сантиметрах:",reply_markup=remove_keyboard)
                await state.set_state(InputData.plaster_thickness)
                return
            else:
                count_floor = list(data["count_floor"])
                await state.update_data(count_window=0, count_walls=0,count_room=0 )
                await message.answer("Выберите этаж с которого хотите начать замер",
                                     reply_markup=choosing_floor(count_floor))
                await state.set_state(InputData.start_floor)

    except ValueError:
        await message.answer("Сообщение должно быть числом")
        return

    finally:
        if data["count_floor"] == []:
            return






# #Заполняем оставшиеся данные и заканчиваем или запоняем новый этаж
# @router.message(InputData.finish_floor)
# async def create_object(message: Message,state: FSMContext):
#     if message.text == "Добавить среднюю толщину штукатурки, коментарии к объекту и закончить":
#         await message.answer("Введите среднюю толщину штукатурки:", reply_markup=remove_keyboard)
#         await state.set_state(InputData.plaster_thickness)
#
#     elif message.text == "Заполнить другой этаж":
#         data = await state.get_data()
#         count_floor = list(data["count_floor"])
#
#         await message.answer("Выберите этаж с которого хотите начать замер",
#                              reply_markup=choosing_floor(count_floor))
#         await state.set_state(InputData.start_floor)
#
#     else:
#         await message.answer("Выберите один из предложенных вариантов")


#Получем среднюю толщину слоя штукатурки
@router.message(InputData.plaster_thickness)
async def create_object(message: Message,state: FSMContext):
    try:
        plaster_thickness = float(message.text)
        if plaster_thickness < 0:
            await message.answer("Число должно быть больше или ровно 0")
            return
        await state.update_data(plaster_thickness=plaster_thickness)
        await message.answer("Введите коментарии:",reply_markup=remove_keyboard)

    except ValueError:
        await message.answer("Сообщение должно быть числом")
        return

    finally:
        if plaster_thickness >= 0:
            await state.set_state(InputData.coment)




#получаем коментарии и выводим резульмат
@router.message(InputData.coment)
async def create_object(message: Message,state: FSMContext):
    await state.update_data(comments=message.text)
    data = await state.get_data()
    await db.append_construction_object(data["construction_object"],plaster_thickness=data['plaster_thickness'],
                                        comments=message.text)
    text = await db.generate_construction_object_report(data["construction_object"])
    await message.answer(
        text,
        reply_markup=remove_keyboard,
        parse_mode="HTML"
    )
    await state.clear()






















