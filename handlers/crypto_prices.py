from aiogram import Router, types, F
from aiogram.filters import Command
from services.crypto_service import get_crypto_service
import logging

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text == "📊 Курсы криптовалют")
@router.message(Command("prices"))
async def crypto_prices_handler(message: types.Message):
    from keyboards.keyboard import get_crypto_keyboard, get_back_to_menu_keyboard

    try:
        # Не отправляем промежуточное сообщение, а сразу отправляем результат
        service = await get_crypto_service()
        formatted_prices = await service.get_formatted_prices()

        # Отправляем новое сообщение с клавиатурой
        await message.answer(
            formatted_prices,
            reply_markup=get_crypto_keyboard(),
            parse_mode="Markdown"
        )
        logger.info(f"Отправлены курсы валют пользователю {message.from_user.id}")

    except Exception as e:
        logger.error(f"Ошибка получения курсов: {e}")
        await message.answer(
            "❌ Произошла ошибка при получении курсов. Попробуйте позже.",
            reply_markup=get_back_to_menu_keyboard()
        )

@router.message(F.text == "Обновить курсы")
async  def refresh_prices_handler(message: types.Message):
    from keyboards.keyboard import get_crypto_keyboard

    try:
        service = await get_crypto_service()
        formatted_prices = await service.get_formatted_prices()

        # Отправляем новое сообщение вместо редактирования
        await message.answer(
            formatted_prices,
            reply_markup=get_crypto_keyboard(),
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Ошибка обновления курсов: {e}")
        await message.answer("❌ Ошибка обновления")


@router.message(F.text == "Назад в меню")
async def back_to_menu_handler(message: types.Message):
    from keyboards.keyboard import get_main_keyboard
    await message.answer(
        "Главное меню:",
        reply_markup=get_main_keyboard()
    )