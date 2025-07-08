from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    objects: fields.ReverseRelation["ConstructionObject"]  # Связь с объектами пользователя

    class Meta:
        table = "users"  # Название таблицы в БД


class ConstructionObject(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="objects")  # Владелец объекта
    address = fields.CharField(max_length=200, null=True)  # Адрес объекта (например, "ул. Строителей, 15")
    plaster_thickness = fields.FloatField(null=True)  # Средняя толщина слоя штукатурки (в мм)
    comments = fields.TextField(null=True, max_length=200)
    floors: fields.ReverseRelation["Floor"]  # Связь с этажами объекта

    async def generate_report(self) -> list:
        total_area = []
        cement_area = []
        gypsum_area = []
        delite_area = []
        number_arched_slopes = []
        number_slopes = []
        full_linear_meters = []
        data_list = []
        report_list = []

        data_list.append(f"Отчет по объекту: {self.address}")
        data_list.append("Введенные данные:")
        data_list.append(f"Средняя толщина слоя штукатурки: {self.plaster_thickness} см")

        report_list.append("Результат:")

        floors = await self.floors.all().order_by("id")
        for index_floor, floor in enumerate(floors, start=1):
            data_list.append(f"Этаж №{index_floor}")
            report_list.append(f"Этаж №{index_floor}")
            floor_cement_area = 0.0
            floor_gypsum_area = 0.0
            floor_total_area = 0.0
            floor_delite_area = 0.0
            floor_number_slopes = 0.0
            floor_number_arched_slopes = 0
            rooms = await floor.rooms.all().order_by("id")
            for index_room, room in enumerate(rooms, start=1):

                data_list.append(f"   Комната №{index_room}")
                data_list.append(f"     Доп. площадь: {room.extra_wall_area} м")
                data_list.append(f"     Тип штукатурки: {room.extra_wall_area}")
                data_list.append(f"     Погонные метры: {room.linear_meters} м")

                walls = await room.walls.all().order_by("id")
                windows = await room.windows.all().order_by("id")

                for index_wall, wall in enumerate(walls, start=1):

                    data_list.append(f"     Стены №{index_wall}")
                    data_list.append(f"         Периметр стен: {wall.perimeter} м")
                    data_list.append(f"         Высота стен: {wall.height} м")

                    area = await wall.get_area()
                    floor_total_area += area
                    if room.extra_wall_area == "Цементная":
                        floor_cement_area += area

                    else:
                        floor_gypsum_area += area

                for index_window, window in enumerate(windows, start=1):
                    data_list.append(f"     Окна №{index_window}")
                    data_list.append(f"         Ширина окна: {window.width} м")
                    data_list.append(f"         Высота окна: {window.height} м")
                    data_list.append(f"         Нужна ли штукатурка откосов: {"Да" if window.needs_plaster else "Нет"}")
                    data_list.append(
                        f"          Оштукатурить все 4 стороны: {"Да" if window.plaster_all_sides else "Нет"}")
                    data_list.append(f"         Арочное окно: {"Да" if window.is_arched else "Нет"}")
                    data_list.append(f"         Только 2 стороны: {"Да" if window.plaster_two_sides else "Нет"}")
                    area = await window.get_area()
                    floor_delite_area += area
                    floor_total_area -= area
                    if room.extra_wall_area == "Цементная":
                        floor_cement_area -= area

                    else:
                        floor_gypsum_area -= area
                    #Считаем откосы
                    if window.needs_plaster:
                         pass
                    elif window.plaster_all_sides:
                        floor_number_slopes += 2*(window.width + window.height)
                    elif window.is_arched:
                        floor_number_arched_slopes += 1
                    else:
                        floor_number_slopes += window.height * 2

                floor_delite_area += room.door_area
                if room.extra_wall_area == "Цементная":
                    floor_cement_area -= room.door_area

                else:
                    floor_gypsum_area -= room.door_area
                #Заполняем в общее
                total_area.append(floor_total_area)
                cement_area.append(floor_cement_area)
                gypsum_area.append(floor_gypsum_area)
                delite_area.append(floor_delite_area)
                number_slopes.append(floor_number_slopes)
                number_arched_slopes.append(floor_number_slopes)
                full_linear_meters.append(room.linear_meters)
                #Выводим результаты этажа
                report_list.append(f"   Общая площадь этажа: {floor_total_area} м²")
                report_list.append(f"   Площадь цементной штукатурки: {floor_cement_area} м²")
                report_list.append(f"   Площадь гипсовой штукатурки: {floor_gypsum_area} м²")
                report_list.append(f"   Вычисленная площадь проемов: {floor_delite_area} м²")
                report_list.append(f"   Количество откосов: {floor_number_slopes} м")
                report_list.append(f"   Количество арочных откосов: {floor_number_arched_slopes}")
                report_list.append(f"   Количество погонных метров: {room.linear_meters} м")
                #Обнуляем
                floor_cement_area = 0.0
                floor_gypsum_area = 0.0
                floor_total_area = 0.0
                floor_delite_area = 0.0
                floor_number_slopes = 0.0
                floor_number_arched_slopes = 0

        data_list.append(f"Комментарии: {self.comments}")

        report_list.append("Общие данные объекта:")
        report_list.append(f"   Общая площадь стен: {sum(total_area)} м²")
        report_list.append(f"   Площадь цементной штукатурки: {sum(cement_area)} м²")
        report_list.append(f"   Площадь гипсовой штукатурки: {sum(gypsum_area)} м²")
        report_list.append(f"   Вычисленная площадь проемов: {sum(delite_area)} м²")
        report_list.append(f"   Количество откосов: {sum(number_slopes)} м")
        report_list.append(f"   Количество арочных откосов: {sum(number_arched_slopes)}")
        report_list.append(f"   Количество погонных метров: {sum(full_linear_meters)} м")

        return ["\n".join(data_list), "\n".join(report_list)]

    class Meta:
        table = "construction_objects"


class Floor(Model):
    id = fields.IntField(pk=True)
    object = fields.ForeignKeyField("models.ConstructionObject", related_name="floors")  # Привязка к объекту

    rooms: fields.ReverseRelation["Room"]  # Связь с комнатами на этаже

    class Meta:
        table = "floors"


class Room(Model):
    id = fields.IntField(pk=True)
    floor = fields.ForeignKeyField("models.Floor", related_name="rooms")  # Привязка к этажу
    # Площадь дверных проемов (в м²)
    walls: fields.ReverseRelation["Wall"]  # Связь со стенами комнаты
    extra_wall_area = fields.FloatField(default=0.0, null=True)  # Доп. площадь (например, выступы)
    plaster_type = fields.CharField(max_length=20, null=True)  # Тип штукатурки
    linear_meters = fields.FloatField(default=0.0, null=True)  # Погонные метры (для углов, откосов)

    windows: fields.ReverseRelation["Window"]  # Связь с окнами комнаты

    door_area = fields.FloatField(default=0.0)

    async def get_data(self):
        data_list_room = []
        data_list_walls = []
        data_list_windows = []

        str_walls = []
        str_windows = []

        data_list_room.append(f"Комната")
        data_list_room.append(f"     Доп. площадь: {self.extra_wall_area} м")
        data_list_room.append(f"     Тип штукатурки: {self.extra_wall_area}")
        data_list_room.append(f"     Погонные метры: {self.linear_meters} м")
        str_room = "\n".join(data_list_room)

        walls = await self.walls.all().order_by("id")
        windows = await self.windows.all().order_by("id")


        for index_wall, wall in enumerate(walls, start=1):

            str_walls.append(f"Стены №{index_wall}")
            str_walls.append(f"     Периметр стен: {wall.perimeter} м")
            str_walls.append(f"     Высота стен: {wall.height} м")
            data_list_walls.append("\n".join(str_walls))
            str_walls = []

        for index_window, window in enumerate(windows, start=1):
            str_windows.append(f"Окна №{index_window}")
            str_windows.append(f"     Ширина окна: {window.width} м")
            str_windows.append(f"     высота окна: {window.height} м")
            str_windows.append(f"     Нужна ли штукатурка откосов: {"Да" if window.needs_plaster else "Нет"}")
            str_windows.append(f"     Оштукатурить все 4 стороны: {"Да" if window.plaster_all_sides else "Нет"}")
            str_windows.append(f"     Арочное окно: {"Да" if window.is_arched else "Нет"}")
            str_windows.append(f"     Только 2 стороны: {"Да" if window.plaster_two_sides else "Нет"}")
            data_list_windows.append("\n".join(str_windows))
            str_windows = []

        return str_room, data_list_walls,data_list_windows

    class Meta:
        table = "rooms"


class Wall(Model):
    id = fields.IntField(pk=True)
    room = fields.ForeignKeyField("models.Room", related_name="walls")  # Привязка к комнате
    perimeter = fields.FloatField()  # Периметр стен (в метрах)
    height = fields.FloatField()  # Высота потолков (в метрах)

    async def get_area(self):
        return self.perimeter * self.height

    class Meta:
        table = "walls"


class Window(Model):
    id = fields.IntField(pk=True)
    room = fields.ForeignKeyField("models.Room", related_name="windows")  # Привязка к комнате
    width = fields.FloatField()  # Ширина окна (в метрах)
    height = fields.FloatField()  # Высота окна (в метрах)
    needs_plaster = fields.BooleanField(default=True)  # Нужна ли штукатурка откосов?
    plaster_all_sides = fields.BooleanField(default=False)  # Оштукатурить все 4 стороны
    is_arched = fields.BooleanField(default=False)  # Арочное окно
    plaster_two_sides = fields.BooleanField(default=False)  # Только 2 стороны

    async def get_area(self):
        return self.width * self.height

    class Meta:
        table = "windows"

# Адрес объекта
# Количество этажей
# Отметить галочками если меется подвал или мансарда НЕ ОБЯЗАТЕЛЬНО
# Выберите этаж с которого хотите начать замер
# Данные для этажа
#     Данные комнаты
#         Данные стен
#             Введите периметр стен
#             Введите высоту потолков
#
#
#         Добавить дополнительную площадь стен,
#         Выбрать циментную  штукатурку или гипсовою штукатурку
#         Введите количесвто погонных метров
#
#         Данные окон
#             Ширина окана
#             Высота окна
#             Необходима штукатурка откосов
#             Неоходимо оштукатурить с четырех сторон
#             Окна арочной формы
#             Штукатурка только с двух сторон
#         Дверной проем площадь
#
# Завершаем замер
#     Введите среднюю толщину слоя для подсчета необходимого кол-во материала
#
#
# Вывод подсчета
#     По этажам
#         Общая площадь стен и откосов
#         Площадь гопсовой штукатурки
#         Площадь цементной штукатурки
#         Вычтеная площадь проемов
#         Кол-во откосов
#         Кол-во фрочных откосов
#         Кол-во погонных метров
#     Общее
#         Общая площадь стен и откосов
#         Площадь гопсовой штукатурки
#         Площадь цементной штукатурки
#         Вычтеная площадь проемов
#         Кол-во откосов
#         Кол-во фрочных откосов
#         Кол-во погонных метров
#         ТОлщина слоя
#     +
#         гипсовая штукатурка в мешках
#         Цементная штукатурка в мешках
#         Мояки
#         Внешнии углы
#         грунтовка
#
# =>
#
#
#     |
#     модель обьекта
#         |
#         модель этажа
#             |
#             модель комнат
#                 |
#                 модель стен
#                     |
#                     периметр стен
#                     высоту потолков
#
#                 дополнительная площадь стен
#                 вид шукатурки
#                 погонные метры
#
#                 модель окон
#                     |
#                     Ширина окана
#                     Высота окна
#                     Необходима штукатурка откосов
#                     Неоходимо оштукатурить с четырех сторон
#                     Окна арочной формы
#                     Штукатурка только с двух сторон
#         средняя толщина слоя
#         коментарии к проекту
