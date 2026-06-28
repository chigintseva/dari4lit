Python
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Токен берется из настроек Render
TOKEN = os.getenv("8856886255:AAGjqIc2glu83RFQFHFW2eQBdPFRwZ-L19U")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привет! Я ваш семейный бот, запущенный на Render!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
