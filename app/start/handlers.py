from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from config.logging_admin import loger

from app.database.repository import db

from app.start.keyboards import *
from app.start.state_fms import StateFmsStart

router = Router()

@router.message(Command("start"))
async def start(message: Message):
    await message.answer("Бот создан для расчета площади и строительного материала"
                         "Вы можете либо просмотреть, изменить данные в существующем объекте"
                         "либо создать новый проект",reply_markup=start_keyboard)