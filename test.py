from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode

bot = Bot(token="YOUR_TOKEN")
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
