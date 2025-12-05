import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class BotConfig:
    token: str
    coingecko_api_key: Optional[str] = None  # Добавляем это поле

    cryptocurrencies: tuple = ("bitcoin", "ethereum", "cardano", "solana",
                               "ripple", "polkadot", "dogecoin", "litecoin",
                               "chainlink", "matic-network")


def load_config() -> BotConfig:
    token = os.getenv("BOT_TOKEN")

    if not token:
        raise ValueError("BOT_TOKEN не найден в .env файле")

    return BotConfig(
        token=token,
        coingecko_api_key=os.getenv("COINGECKO_API_KEY")  # Добавляем опциональный ключ
    )