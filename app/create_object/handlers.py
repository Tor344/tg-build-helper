from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from config.logging_admin import loger

from app.database.repository import db

from app.start.keyboards import *
from app.start.state_fms import StateFmsStart

router = Router()

@router.message(F.text == "Создать объект")
async def create_object(message: Message):
    await message.answer("",reply_markup=start_keyboard)