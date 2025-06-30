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
    await message.answer("Введите адрес объекта",reply_markup=remove_keyboard)
    await state.set_state(InputData.name_object)


#получаем адрес
@router.message(InputData.name_object)
async def create_object(message: Message,state: FSMContext):
    await state.update_data({"name_object": message.text})
    await message.answer("Введите количество этажей")

    await state.set_state(InputData.count_floor)


#получем количество этажей
@router.message(InputData.count_floor)
async def create_object(message: Message,state: FSMContext):
    if not(message.text.isdigit()):
        await message.answer("Сообщение должно быть числом")
        return

    await state.update_data(count_floor = int(message.text))
    await message.answer("Выберите этаж с которого хотите начать замер",reply_markup=choosing_floor(int(message.text)))

    await state.set_state(InputData.start_floor)


#получем стартовый этаж
@router.message(InputData.start_floor)
async def create_object(message: Message,state: FSMContext):
    if not(message.text.isdigit()):
        await message.answer("Сообщение должно быть числом")
        return

    await state.update_data(number_floor=int(message.text))
    await message.answer("Начинаем вносить данные для комнаты\n"
                        "Введите периметр стен",reply_markup=remove_keyboard)

    await state.set_state(InputData.walls_perimeter)


#получем периметр стен
@router.message(InputData.walls_perimeter)
async def create_object(message: Message,state: FSMContext):
    try:
        perimeter = float(message.text)
        if perimeter < 0:
            await message.answer("Число должно быть больше или ровно 0")
            return
        await state.update_data(walls_perimeter=perimeter)
        await message.answer("Введите высоту потолков")

    except ValueError:
        await message.answer("Сообщение должно быть числом")
        return

    finally:
        if perimeter >= 0:
            await state.set_state(InputData.finish_walls)


#добавляем еще одну стену или продолжаем заполнение
@router.message(InputData.finish_walls)
async def create_object(message: Message,state: FSMContext):
    try:
        height = float(message.text)
        if height < 0:
            await message.answer("Число должно быть больше или ровно 0")
            return

        await state.update_data(walls_height=height)
        await message.answer("Выберите один из вариантов",reply_markup=finish_walls)
    except ValueError:
        await message.answer("Сообщение должно быть числом")
        return

    finally:
        if height >= 0:
            await state.set_state(InputData.input_status_walls)


#получаем высоту потолков или возврашаем на запонение еще одной стены
@router.message(InputData.input_status_walls)
async def create_object(message: Message,state: FSMContext):
    if message.text == "Продолжить":
        await message.answer("Введите доп. площадь стен",reply_markup=remove_keyboard)
        await state.set_state(InputData.extra_wall_area)
    elif message.text == "Добавить стены с другой высотой":
        await message.answer("Добавление еще одной стены\n"
                             "Введите периметр стен", reply_markup=remove_keyboard)
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
        await message.answer("Выберите тип штукатурки",reply_markup=type_plaster)

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
        await message.answer("Выберите один из предложенных вариантов")
        return
    await state.update_data(plaster_type=message.text)
    await message.answer("Введите погонные метры",reply_markup=remove_keyboard)
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
        await message.answer("Введите ширину окна")

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
        await message.answer("Введите высоту окна")

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
    if message.text == "Продолжить":
        await message.answer("Введите площадь дверного проема",reply_markup=remove_keyboard)
        await state.set_state(InputData.door_area)
    elif message.text == "Добавить окно":
        await message.answer("Добавление еще одного окна\n"
                             "Введите высоту окна", reply_markup=remove_keyboard)
        await state.set_state(InputData.window_width)
    else:
        await message.answer("Выберите один из предложенных вариантов")


#получаем площадь дверного проема
@router.message(InputData.door_area)
async def create_object(message: Message,state: FSMContext):
    try:
        door_area = float(message.text)
        if door_area < 0:
            await message.answer("Число должно быть больше или ровно 0")
            return
        await state.update_data(door_area=door_area)
        await message.answer("Выберите один из вариантов:",reply_markup=finish_floor)

    except ValueError:
        await message.answer("Сообщение должно быть числом")
        return

    finally:
        if door_area >= 0:
            await state.set_state(InputData.finish_floor)





#Заполняем оставшиеся данные и заканчиваем или запоняем новый этаж
@router.message(InputData.finish_floor)
async def create_object(message: Message,state: FSMContext):
    if message.text == "Добавить среднюю толщину штукатурки, коментарии к объекту и закончить":
        await message.answer("Введите среднюю толщину штукатурки:", reply_markup=remove_keyboard)
        await state.set_state(InputData.plaster_thickness)

    elif message.text == "Заполнить другой этаж":
        data = await state.get_data()
        await message.answer("Выберите этаж с которого хотите начать замер",
                             reply_markup=choosing_floor(int(data["count_floor"])))
        await state.set_state(InputData.start_floor)

    else:
        await message.answer("Выберите один из предложенных вариантов")


#Получем среднюю толщину слоя штукатурки
@router.message(InputData.plaster_thickness)
async def create_object(message: Message,state: FSMContext):
    try:
        plaster_thickness = float(message.text)
        if plaster_thickness < 0:
            await message.answer("Число должно быть больше или ровно 0")
            return
        await state.update_data(plaster_thickness=plaster_thickness)
        await message.answer("Добавить коментарии:",reply_markup=remove_keyboard)

    except ValueError:
        await message.answer("Сообщение должно быть числом")
        return

    finally:
        if plaster_thickness >= 0:
            await state.set_state(InputData.coment)





@router.message(InputData.coment)
async def create_object(message: Message,state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data()

    formatted_data = "\n".join(
        f"<b>{key}:</b> {value}"
        for key, value in data.items()
    )
    await message.answer(
        f"Вы закончили заполнять данные:\n{formatted_data}",
        reply_markup=remove_keyboard,
        parse_mode="HTML"
    )
    await state.clear()






















