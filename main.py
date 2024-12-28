from engine.async_executor import AsyncExecutor
from engine.aiogram_system import AiogramSystem

from storage_systems import SYSTEMS as STORAGE_SYSTEMS
from telegram_systems import SYSTEMS as TELEGRAM_SYSTEMS

import config


def main() -> None:
    aiogram_system = AiogramSystem()
    aiogram_system.add_bot(
        config.KARNAUKHIVKA_LOCATIONS_BOT, config.TOKEN
    )

    AsyncExecutor(
        STORAGE_SYSTEMS + TELEGRAM_SYSTEMS + [
            aiogram_system
        ]
    ).start()


if __name__ == "__main__":
    main()
