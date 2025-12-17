from aiogram import Router, types, F
from aiogram.filters import Command
from data.database import get_user_alerts, delete_alert, set_alert
import re

router = Router()


@router.message(F.text == "🔔 Мои уведомления")
@router.message(Command("alerts"))
async def alerts_menu(message: types.Message):
    user_alerts = get_user_alerts(message.from_user.id)

    alert_text = "🔔 *Ваши текущие уведомления:*\n\n"

    if user_alerts:
        for alert in user_alerts:
            user_id, btc_threshold, eth_threshold, is_active = alert
            if btc_threshold:
                alert_text += f"• BTC > ${btc_threshold:,.0f}\n"
            if eth_threshold:
                alert_text += f"• ETH > ${eth_threshold:,.0f}\n"
    else:
        alert_text += "❌ У вас нет активных уведомлений\n"

    alert_text += "\n👇 *Выберите действие:*"

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📋 Мои уведомления")],
            [types.KeyboardButton(text="📈 BTC > 50000")],
            [types.KeyboardButton(text="📈 ETH > 3000")],
            [types.KeyboardButton(text="❌ Удалить все уведомления")],
            [types.KeyboardButton(text="Назад в меню")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        alert_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.message(F.text == "📋 Мои уведомления")
async def show_my_alerts_simple(message: types.Message):
    user_alerts = get_user_alerts(message.from_user.id)

    if not user_alerts:
        await message.answer("❌ У вас нет активных уведомлений")
        return

    alert_text = "📋 *Ваши активные уведомления:*\n\n"

    for alert in user_alerts:
        user_id, btc_threshold, eth_threshold, is_active = alert

        if btc_threshold:
            alert_text += f"• BTC > ${btc_threshold:,.0f}\n"

        if eth_threshold:
            alert_text += f"• ETH > ${eth_threshold:,.0f}\n"

    alert_text += "\nЧтобы удалить уведомления, используйте:\n"
    alert_text += "• 'Удалить BTC' - для удаления BTC уведомлений\n"
    alert_text += "• 'Удалить ETH' - для удаления ETH уведомлений\n"
    alert_text += "• '❌ Удалить все уведомления' - кнопка выше"

    await message.answer(alert_text, parse_mode="Markdown")


@router.message(F.text.regexp(r'(?i)удалить\s+btc'))
async def delete_btc_alert(message: types.Message):
    delete_alert(message.from_user.id, 'btc')
    await message.answer("✅ Все уведомления BTC удалены!")


@router.message(F.text.regexp(r'(?i)удалить\s+eth'))
async def delete_eth_alert(message: types.Message):
    delete_alert(message.from_user.id, 'eth')
    await message.answer("✅ Все уведомления ETH удалены!")


@router.message(F.text == "📈 BTC > 50000")
async def set_btc_alert(message: types.Message):
    set_alert(message.from_user.id, btc_threshold=50000)
    await message.answer("✅ Уведомление для BTC установлено на $50,000")


@router.message(F.text == "📈 ETH > 3000")
async def set_eth_alert(message: types.Message):
    set_alert(message.from_user.id, eth_threshold=3000)
    await message.answer("✅ Уведомление для ETH установлено на $3,000")


@router.message(F.text == "❌ Удалить все уведомления")
async def delete_all_alerts(message: types.Message):
    delete_alert(message.from_user.id)
    await message.answer("✅ Все ваши уведомления удалены!")


@router.message(F.text.regexp(r'(?i)(btc|eth)\s*[<>]\s*\d+'))
async def set_custom_alert(message: types.Message):
    text = message.text.lower()

    if 'btc' in text:
        numbers = re.findall(r'\d+', text)
        if numbers:
            threshold = float(numbers[0])
            set_alert(message.from_user.id, btc_threshold=threshold)
            await message.answer(f"✅ Уведомление для BTC установлено на ${threshold:,.0f}")
        else:
            await message.answer("❌ Не могу найти число. Пример: 'BTC > 50000'")

    elif 'eth' in text:
        numbers = re.findall(r'\d+', text)
        if numbers:
            threshold = float(numbers[0])
            set_alert(message.from_user.id, eth_threshold=threshold)
            await message.answer(f"✅ Уведомление для ETH установлено на ${threshold:,.0f}")
        else:
            await message.answer("❌ Не могу найти число. Пример: 'ETH < 3000'")


@router.message(F.text == "Назад в меню")
async def back_to_menu(message: types.Message):
    from keyboards.keyboard import get_main_keyboard
    await message.answer("Главное меню:", reply_markup=get_main_keyboard())