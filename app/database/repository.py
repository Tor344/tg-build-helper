from tortoise import Tortoise

from app.database.models import *


class Database:
    def __init__(self, db_url: str = "sqlite://db.sqlite3") -> None:
        self.db_url = db_url

    async def connect(self) -> None:
        """Конектимся к базе"""
        await Tortoise.init(db_url=self.db_url, modules={"models": ["app.database.models"]})
        await Tortoise.generate_schemas()

    async def close(self):
        """Закрываем конект"""
        await Tortoise.close_connections()


    async def add_user(self, user_id: int) -> User:
        """Добавляем пользователя, если его нет"""
        exists = await User.filter(id=user_id).exists()
        if not exists:
            user = await User.create(id=user_id)
        else:
            user = await User.get(id=user_id)
        return user

    async def add_construction_object(self, user, address: str) -> ConstructionObject:
        """создает новый обьект user: id пользователя или сам объект,
         id: обьекта будет создаваться самостоятельно,
         address: адрес обьекта """
        user = await User.filter(id=user).first()
        object = await ConstructionObject.create(user=user, address=address)
        return object

    async def append_construction_object(self,object,plaster_thickness:float,comments:str):
        object.plaster_thickness = plaster_thickness
        object.comments = comments
        await object.save()
        return object





    async def add_floor(self, object: int) -> Floor:
        """создаем этаж id_object: объект или id его"""
        floor = await Floor.create(object=object)
        return floor

    async def add_room(self, floor) -> Room:
        room = await Room.create(floor=floor)
        return room

    async def append_room(self, room, extra_wall_area: float, plaster_type: str,
                          linear_meters: float, door_area: float) -> Room:
        room.extra_wall_area = extra_wall_area# Доп. площадь (например, выступы)
        room.plaster_type = plaster_type# Тип штукатурки
        room.linear_meters = linear_meters# Погонные метры (для углов, откосов)
        room.door_area = door_area# Площадь дверного проема
        await room.save()
        return room


    async def add_wall(self, room, perimeter: float, height: float) -> Wall:
        wall = await Wall.create(room=room, perimeter=perimeter, height=height)
        return wall

    async def add_window(self, room, width: float, height: float, data_window: list) -> Window:
        window = await Window.create(room=room, width=width,
                                     height=height, needs_plaster=data_window[0],
                                     plaster_all_sides=data_window[1],
                                     is_arched=data_window[2], plaster_two_sides=data_window[3]
                                     )
        return window



    async def get_user(self, user_id: int):
        """получем данные пользователя"""
        return await User.get_or_none(id=user_id)

    async def update_user(self, user_id: int, user_name: str, age: int) -> None:
        """Изменяет или добавляет пользователя"""
        await User.update_or_create(id=user_id, user_name=user_name, age=age)

    async def delete_user(self, user_id: int) -> bool:
        """Удоляем пользователя True если удалили False если нет"""
        return bool(await User.filter(user_id=user_id).delete())

    async def generate_construction_object_report(self, obj: ConstructionObject) -> str:
        # Загружаем связанные данные
        await obj.fetch_related(
            "floors__rooms__walls",
            "floors__rooms__windows",
            "user"
        )

        report_lines = []
        report_lines.append(f"ОТЧЁТ ПО ОБЪЕКТУ: {obj.address or 'Без названия'}")
        report_lines.append(f"ID объекта: {obj.id}")
        report_lines.append(f"Толщина штукатурки: {obj.plaster_thickness} мм")
        report_lines.append(f"Комментарии: {obj.comments}")
        report_lines.append("=" * 50)

        total_object_area = 0.0

        # Сортируем этажи по ID
        floors = await obj.floors.all().order_by('id')
        for floor_idx, floor in enumerate(floors, 1):
            report_lines.append(f"\nЭТАЖ #{floor_idx} (ID: {floor.id})")
            total_floor_area = 0.0

            # Сортируем комнаты по ID
            rooms = await floor.rooms.all().order_by('id')
            for room in rooms:
                report_lines.append(f"\n  КОМНАТА ID: {room.id}")
                report_lines.append(f"  - Тип штукатурки: {room.plaster_type}")
                report_lines.append(f"  - Доп. площадь стен: {room.extra_wall_area} м²")
                report_lines.append(f"  - Погонные метры: {room.linear_meters} м")
                report_lines.append(f"  - Площадь дверей: {room.door_area} м²")

                # Рассчитываем площадь комнаты
                room_wall_area = 0.0
                window_area = 0.0

                # Обработка стен
                walls = await room.walls.all()
                for wall in walls:
                    wall_area = wall.perimeter * wall.height
                    room_wall_area += wall_area
                    report_lines.append(
                        f"  - Стена ID:{wall.id}: {wall.perimeter}м x {wall.height}м = {wall_area:.2f}м²")

                # Обработка окон
                windows = await room.windows.all()
                for window in windows:
                    win_area = window.width * window.height
                    window_area += win_area
                    report_lines.append(
                        f"  - Окно ID:{window.id}: {window.width}м x {window.height}м = {win_area:.2f}м²"
                        f" [Штукатурка: {'Да' if window.needs_plaster else 'Нет'}]"
                    )

                # Финанльная площадь комнаты с учётом вычетов
                room_total = room_wall_area + room.extra_wall_area - window_area - room.door_area
                report_lines.append(f"  ИТОГО ДЛЯ КОМНАТЫ: {room_total:.2f} м²")
                total_floor_area += max(room_total, 0)  # Защита от отрицательных значений

            report_lines.append(f"\nОБЩАЯ ПЛОЩАДЬ ЭТАЖА #{floor_idx}: {total_floor_area:.2f} м²")
            total_object_area += total_floor_area

        report_lines.append("=" * 50)
        report_lines.append(f"ОБЩАЯ ПЛОЩАДЬ ОБЪЕКТА: {total_object_area:.2f} м²")
        return "\n".join(report_lines)
db = Database()


if __name__ == "__main__":
    pass


