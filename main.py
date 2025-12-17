import asyncio
import logging
import colorlog
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from config import load_config
from handlers.help_service import router as help_router
from handlers.alerts import router as alerts_router
from services.alert_checker import AlertChecker


# Настройка цветного логирования
def setup_colored_logging():
    # Создаем цветной форматтер
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',  # ЗЕЛЕНЫЙ для информационных сообщений
            'WARNING': 'yellow',
            'ERROR': 'red',  # КРАСНЫЙ для ошибок
            'CRITICAL': 'red,bg_white',
        },
        reset=True,
        style='%'
    )

    # Настраиваем консольный handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Получаем root логгер и настраиваем его
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Удаляем старые handlers
    root_logger.handlers = []

    # Добавляем наш цветной handler
    root_logger.addHandler(console_handler)

    # Также можно настроить файловый логгер (опционально)
    file_handler = logging.FileHandler('bot.log', encoding='utf-8')
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)


# Импортируем хендлеры
from handlers.start import router as start_router
from handlers.crypto_prices import router as crypto_router
from services.crypto_service import get_crypto_service


async def background_price_updater():
    """Фоновая задача для обновления цен раз в минуту"""
    logger = logging.getLogger(__name__)
    logger.info("💚 Запуск фонового обновления цен...")

    try:
        service = await get_crypto_service()

        while True:
            try:
                # Обновляем цены
                await service.get_all_prices(force_update=False)
                logger.debug("✅ Цены успешно обновлены")

            except Exception as e:
                logger.error(f"🔴 Ошибка в фоновом обновлении: {e}")

            # Ждем 60 секунд перед следующим обновлением
            await asyncio.sleep(60)

    except asyncio.CancelledError:
        logger.info("⏹️ Фоновая задача остановлена")
    except Exception as e:
        logger.error(f"🔴 Критическая ошибка в фоновой задаче: {e}")


async def main() -> None:
    # Настраиваем цветное логирование
    setup_colored_logging()

    config = load_config()

    # Инициализация бота
    storage = MemoryStorage()
    bot = Bot(token=config.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=storage)

    # Подключаем роутеры
    dp.include_router(start_router)
    dp.include_router(crypto_router)
    dp.include_router(help_router)
    dp.include_router(alerts_router)

    # Запускаем фоновую задачу
    background_task = asyncio.create_task(background_price_updater())
    alert_checker = AlertChecker(bot)
    checker_task = asyncio.create_task(alert_checker.run_checker())

    try:
        logger = logging.getLogger(__name__)
        logger.info("🤖 Бот запущен и готов к работе!")
        await dp.start_polling(bot)
    finally:
        # Останавливаем фоновую задачу при завершении
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            pass

        logger.info("🛑 Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())