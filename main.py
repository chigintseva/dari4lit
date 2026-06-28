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

# Базы данных в памяти
shopping_list = []
users = set()  # Храним ID людей, которые нажали /start

# Кнопки
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛒 Посмотреть список"), KeyboardButton(text="📩 Отправить просьбу")],
        [KeyboardButton(text="🗑 Очистить всё")]
    ],
    resize_keyboard=True
)

# Веб-сервер для "успокоения" Render
async def handle(request):
    return aiohttp.web.Response(text="Bot is running")

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    users.add(message.from_user.id)  # Запоминаем ID того, кто нажал старт
    await message.answer("Привет! Я твой семейный помощник.\n"
                         "Используй кнопки для управления списком или пересылки просьб.", 
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

@dp.message(F.text == "📩 Отправить просьбу")
async def ask_request(message: types.Message):
    await message.answer("Напиши текст просьбы, и я отправлю его другому пользователю:")

@dp.message(F.text & ~F.text.startswith("/") & ~F.text.in_({"🛒 Посмотреть список", "🗑 Очистить всё", "📩 Отправить просьбу"}))
async def handle_text(message: types.Message):
    # Если в списке нет других пользователей, кроме отправителя
    other_users = [u for u in users if u != message.from_user.id]
    
    # Логика: если отправили просьбу, а не продукт
    if not other_users:
        # Добавляем в список покупок, если нет адресата для просьбы
        shopping_list.append(message.text)
        await message.answer(f"✅ Добавлено в список покупок: {message.text}")
    else:
        # Отправляем всем остальным
        for user_id in other_users:
            try:
                await bot.send_message(user_id, f"🔔 Просьба от {message.from_user.first_name}:\n\n{message.text}")
                await message.answer("✅ Отправлено другому пользователю!")
            except:
                await message.answer("Не удалось отправить просьбу.")

async def main():
    # Запуск веб-сервера
    app = aiohttp.web.Application()
    app.router.add_get("/", handle)
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000))
    site = aiohttp.web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Веб-сервер запущен на порту {port}!")
    
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
