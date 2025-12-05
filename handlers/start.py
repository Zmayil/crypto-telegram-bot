from aiogram import Router, types
from aiogram.filters import Command
from keyboards import get_main_keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Добро пожаловать!",
        reply_markup=get_main_keyboard(),
    )

@router.message(Command("help"))
async def cmd_help(message: types.Message) -> None:
       await message.answer(
        "📋 Доступные команды:\n"
        "/start - Начать работу\n"
        "/help - Помощь\n"
    )