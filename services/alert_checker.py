import asyncio
import logging
from data.database import get_active_alerts
from services.crypto_service import get_crypto_service

logger = logging.getLogger(__name__)


class AlertChecker:
    def __init__(self, bot):
        self.bot = bot
        self.triggered_alerts = set()  # Чтобы не спамить

    async def check_alerts(self):
        """Проверяет уведомления и отправляет если нужно"""
        try:
            # Получаем текущие цены
            service = await get_crypto_service()
            prices = await service.get_all_prices()

            if not prices:
                return

            btc_price = prices.get('BTC', {}).get('price', 0)
            eth_price = prices.get('ETH', {}).get('price', 0)

            # Получаем все активные уведомления
            alerts = get_active_alerts()

            for alert in alerts:
                user_id, btc_threshold, eth_threshold, is_active = alert

                alert_key = f"{user_id}_btc_{btc_threshold}_eth_{eth_threshold}"

                # Проверяем BTC
                if btc_threshold and btc_price >= btc_threshold:
                    if alert_key not in self.triggered_alerts:
                        try:
                            await self.bot.send_message(
                                user_id,
                                f"🚀 BTC достиг ${btc_price:,.0f}!\n"
                                f"Порог: ${btc_threshold:,.0f}"
                            )
                            self.triggered_alerts.add(alert_key)
                            logger.info(f"Отправлено уведомление BTC пользователю {user_id}")
                        except Exception as e:
                            logger.error(f"Ошибка отправки уведомления: {e}")

                # Проверяем ETH
                if eth_threshold and eth_price >= eth_threshold:
                    if alert_key not in self.triggered_alerts:
                        try:
                            await self.bot.send_message(
                                user_id,
                                f"🚀 ETH достиг ${eth_price:,.0f}!\n"
                                f"Порог: ${eth_threshold:,.0f}"
                            )
                            self.triggered_alerts.add(alert_key)
                            logger.info(f"Отправлено уведомление ETH пользователю {user_id}")
                        except Exception as e:
                            logger.error(f"Ошибка отправки уведомления: {e}")

        except Exception as e:
            logger.error(f"Ошибка проверки уведомлений: {e}")

    async def run_checker(self):
        """Запускает фоновую проверку"""
        logger.info("Запуск проверки уведомлений...")
        while True:
            try:
                await self.check_alerts()
            except Exception as e:
                logger.error(f"Ошибка в проверке уведомлений: {e}")

            await asyncio.sleep(30)  # Проверяем каждые 30 секунд