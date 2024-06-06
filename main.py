import os
import asyncio
import logging
import sys

from Handlers.comands import router as comands_router
from Handlers.message import router as message_router
from Serv.req import router as serv_router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommandScopeDefault
from KeyBoard.keyboard import comands

from DB.connect_db import connect_to_db

dp = Dispatcher()
conn = connect_to_db()

async def main():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    bot = Bot(token=bot_token,default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_routers(
        comands_router, message_router, serv_router
    )

    await bot.set_my_commands(comands, scope=BotCommandScopeDefault())
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())


