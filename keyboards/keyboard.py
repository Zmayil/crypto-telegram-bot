from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    button_1 = KeyboardButton(text="📊 Курсы криптовалют")
    button_2 = KeyboardButton(text="🔔 Мои уведомления")
    button_3 = KeyboardButton(text="❓ Помощь")
    return ReplyKeyboardMarkup(
        keyboard=[
            [button_1, button_2],
            [button_3]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_crypto_keyboard():
    """Клавиатура для раздела с курсами"""
    button_refresh = KeyboardButton(text="Обновить курсы")
    button_back = KeyboardButton(text="Назад в меню")

    return ReplyKeyboardMarkup(
        keyboard=[
            [button_refresh],
            [button_back]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_back_to_menu_keyboard():
    """Простая кнопка назад"""
    button_back = KeyboardButton(text="Назад в меню")

    return ReplyKeyboardMarkup(
        keyboard=[[button_back]],
        resize_keyboard=True,
        one_time_keyboard=False
    )
