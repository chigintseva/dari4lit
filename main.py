import asyncio
import os
import aiohttp.web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Токен бота
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Список покупок
shopping_list = []

# Создаем кнопки
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛒 Посмотреть список"), KeyboardButton(text="🗑 Очистить всё")]
    ],
    resize_keyboard=True
)

# Веб-сервер для "успокоения" Render
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
    # Игнорируем нажатия кнопок, чтобы не добавлять их в список
    if message.text not in ["🛒 Посмотреть список", "🗑 Очистить всё"]:
        shopping_list.append(message.text)
        await message.answer(f"✅ Добавлено: {message.text}")

async def main():
    # 1. Запускаем веб-сервер, чтобы Render был доволен портом
    app = aiohttp.web.Application()
    app.router.add_get("/", handle)
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    
    # Порт берется из настроек Render (обычно 10000)
    port = int(os.environ.get("PORT", 10000))
    site = aiohttp.web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Веб-сервер запущен на порту {port}!")
    
    # 2. Запускаем бота в фоновом режиме
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
