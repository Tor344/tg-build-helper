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
    address = fields.CharField(max_length=200,null=True)  # Адрес объекта (например, "ул. Строителей, 15")
    plaster_thickness = fields.FloatField(null=True)  # Средняя толщина слоя штукатурки (в мм)
    comments = fields.TextField(null=True,max_length=200)
    floors: fields.ReverseRelation["Floor"]  # Связь с этажами объекта

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
    extra_wall_area = fields.FloatField(default=0.0,null=True)  # Доп. площадь (например, выступы)
    plaster_type = fields.CharField(max_length=20,null=True)  # Тип штукатурки
    linear_meters = fields.FloatField(default=0.0,null=True)  # Погонные метры (для углов, откосов)


    windows: fields.ReverseRelation["Window"]  # Связь с окнами комнаты

    door_area = fields.FloatField(default=0.0)

    class Meta:
        table = "rooms"


class Wall(Model):
    id = fields.IntField(pk=True)
    room = fields.ForeignKeyField("models.Room", related_name="walls")  # Привязка к комнате
    perimeter = fields.FloatField()  # Периметр стен (в метрах)
    height = fields.FloatField()  # Высота потолков (в метрах)

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
