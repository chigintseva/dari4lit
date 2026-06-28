import asyncio
import os
import aiohttp.web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# База списка (временно в памяти)
shopping_list = []

# Создаем кнопки
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛒 Посмотреть список"), KeyboardButton(text="🗑 Очистить всё")]
    ],
    resize_keyboard=True
)

# Веб-сервер для Render
async def handle(request):
    return aiohttp.web.Response(text="Bot is running")

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привет! Я твой семейный помощник.\n"
                         "Просто напиши название продукта, чтобы добавить его, или используй кнопки ниже.", 
                         reply_markup=keyboard)

@dp.message(F.text == "🛒 Посмотреть список")
async def show_list(message: types.Message):
    if not shopping_list:
        await message.answer("Список покупок пуст!")
    else:
        text = "📋 **Ваш список:**\n\n" + "\n".join([f"• {item}" for item in shopping_list])
        await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "🗑 Очистить всё")
async def clear_list(message: types.Message):
    shopping_list.clear()
    await message.answer("Список успешно очищен!")

@dp.message(F.text & ~F.text.startswith("/"))
async def add_item(message: types.Message):
    # Игнорируем нажатия кнопок (они уже обработаны выше)
    if message.text not in ["🛒 Посмотреть список", "🗑 Очистить всё"]:
        shopping_list.append(message.text)
        await message.answer(f"✅ Добавлено: {message.text}")

async def main():
    app = aiohttp.web.Application()
    app.router.add_get("/", handle)
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 8080)))
    await site.start()
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
