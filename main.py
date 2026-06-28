import asyncio
import os
import aiohttp.web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Кусочек, чтобы Render не ругался на порты
async def handle(request):
    return aiohttp.web.Response(text="Bot is running")

shopping_list = []

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привет! Я твой бот-помощник.")

@dp.message(Command("list"))
async def show_list(message: types.Message):
    if not shopping_list:
        await message.answer("Список покупок пуст!")
    else:
        await message.answer("\n".join(shopping_list))

@dp.message(F.text & ~F.text.startswith("/"))
async def add_item(message: types.Message):
    shopping_list.append(message.text)
    await message.answer(f"Добавила: {message.text}")

async def main():
    # Запускаем веб-сервер на порту, который требует Render
    app = aiohttp.web.Application()
    app.router.add_get("/", handle)
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 8080)))
    await site.start()
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
