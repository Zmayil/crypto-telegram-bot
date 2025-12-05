import aiohttp
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os

logger = logging.getLogger(__name__)

class CryptoService:
    def __init__(self, coingecko_api_key: Optional[str] = None):
        self.coingecko_api_key = coingecko_api_key
        self.cache_file = "data/crypto_cache.json"
        self.cache_duration = timedelta(minutes=1)
        self.cache: Dict = {}
        self._last_update: Optional[datetime] = None
        self._session: Optional[aiohttp.ClientSession] = None

        # Популярные криптовалюты
        self.crypto_ids = {
            "bitcoin": "BTC",
            "ethereum": "ETH",
            "cardano": "ADA",
            "solana": "SOL",
            "ripple": "XRP",
            "polkadot": "DOT",
            "dogecoin": "DOGE",
            "litecoin": "LTC",
            "chainlink": "LINK",
            "matic-network": "MATIC"
        }

        os.makedirs("data", exist_ok=True)

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        await self.load_cache()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    async def load_cache(self):
        """Загружаем кэш из файла"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cache = data.get('prices', {})

                    # Проверяем время последнего обновления
                    last_update_str = data.get('last_update')
                    if last_update_str:
                        self._last_update = datetime.fromisoformat(last_update_str)

                    logger.info(f"Кэш загружен, {len(self.cache)} записей")
        except Exception as e:
            logger.error(f"Ошибка загрузки кэша: {e}")
            self.cache = {}

    async def save_cache(self):
        """Сохраняем кэш в файл"""
        try:
            data = {
                'prices': self.cache,
                'last_update': datetime.now().isoformat()
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения кэша: {e}")

    def is_cache_valid(self) -> bool:
        """Проверяем, не устарел ли кэш"""
        if not self._last_update:
            return False

        return datetime.now() - self._last_update < self.cache_duration

    async def get_prices_from_coingecko(self) -> Dict:
        """Получаем цены с CoinGecko"""
        try:
            # Формируем URL
            ids = ",".join(self.crypto_ids.keys())
            url = f"https://api.coingecko.com/api/v3/simple/price"

            params = {
                'ids': ids,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_market_cap': 'false',
                'include_24hr_vol': 'false'
            }

            if self.coingecko_api_key:
                headers = {'x-cg-demo-api-key': self.coingecko_api_key}
            else:
                headers = {}

            async with self._session.get(url, params=params, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()

                    # Преобразуем в удобный формат
                    result = {}
                    for crypto_id, symbol in self.crypto_ids.items():
                        if crypto_id in data:
                            crypto_data = data[crypto_id]
                            result[symbol] = {
                                'price': crypto_data.get('usd', 0),
                                'change_24h': crypto_data.get('usd_24h_change', 0),
                                'source': 'CoinGecko'
                            }

                    logger.info(f"Успешно получены данные с CoinGecko ({len(result)} записей)")
                    return result
                else:
                    logger.warning(f"CoinGecko API error: {response.status}")
                    return {}

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.warning(f"CoinGecko недоступен: {e}")
            return {}

    async def get_prices_from_binance(self) -> Dict:
        """Получаем цены с Binance (резервный источник)"""
        try:
            result = {}

            # Binance требует отдельные запросы для каждой пары
            for crypto_id, symbol in self.crypto_ids.items():
                # Преобразуем id в символ для Binance
                binance_symbol = f"{symbol}USDT"

                try:
                    url = f"https://api.binance.com/api/v3/ticker/24hr"
                    params = {'symbol': binance_symbol}

                    async with self._session.get(url, params=params, timeout=5) as response:
                        if response.status == 200:
                            data = await response.json()

                            result[symbol] = {
                                'price': float(data['lastPrice']),
                                'change_24h': float(data['priceChangePercent']),
                                'source': 'Binance'
                            }

                            # Небольшая задержка чтобы не перегружать API
                            await asyncio.sleep(0.1)

                except Exception as e:
                    logger.debug(f"Ошибка получения {symbol} с Binance: {e}")
                    continue

            if result:
                logger.info(f"Успешно получены данные с Binance ({len(result)} записей)")

            return result

        except Exception as e:
            logger.error(f"Binance недоступен: {e}")
            return {}

    async def get_all_prices(self, force_update: bool = False) -> Dict:
        """Получаем все цены (используем кэш если он актуален)"""

        # Проверяем кэш если не требуется принудительное обновление
        if not force_update and self.is_cache_valid() and self.cache:
            logger.info("Используем кэшированные данные")
            return self.cache

        logger.info("Обновляем данные о ценах...")

        # Пробуем сначала CoinGecko
        prices = await self.get_prices_from_coingecko()

        # Если CoinGecko недоступен, пробуем Binance
        if not prices:
            logger.info("Пробуем получить данные с Binance...")
            prices = await self.get_prices_from_binance()

        # Если получили данные, обновляем кэш
        if prices:
            self.cache = prices
            self._last_update = datetime.now()
            await self.save_cache()
        else:
            logger.error("Не удалось получить данные ни с одного источника")

        return self.cache

    async def get_formatted_prices(self) -> str:
        """Форматируем цены для отображения в сообщении"""
        prices = await self.get_all_prices()

        if not prices:
            return "❌ Не удалось получить данные о курсах криптовалют"

        lines = ["📊 **Курсы криптовалют:**\n"]

        for symbol, data in prices.items():
            price = data['price']
            change = data['change_24h']
            source = data.get('source', 'Unknown')

            # Определяем эмодзи для изменения цены
            if change > 0:
                change_emoji = "📈"
                change_str = f"+{change:.2f}%"
            elif change < 0:
                change_emoji = "📉"
                change_str = f"{change:.2f}%"
            else:
                change_emoji = "➡️"
                change_str = "0.00%"

            # Форматируем цену
            if price >= 1:
                price_str = f"${price:,.2f}"
            else:
                price_str = f"${price:.6f}".rstrip('0').rstrip('.')

            lines.append(f"{change_emoji} **{symbol}:** {price_str} ({change_str})")

        lines.append(f"\n_Обновлено: {datetime.now().strftime('%H:%M:%S')}_")
        lines.append(f"_Источник: {next(iter(prices.values()))['source']}_")

        return "\n".join(lines)


crypto_service: Optional[CryptoService] = None

async def get_crypto_service() -> CryptoService:
    """Получаем экземпляр сервиса (синглтон)"""
    global crypto_service
    if crypto_service is None:
        crypto_service = CryptoService()  # Убрали передачу ключа
        await crypto_service.__aenter__()
    return crypto_service