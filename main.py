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
users = set()       # ID всех, кто нажал /start
user_states = {}    # Режим "ожидания просьбы" для каждого пользователя

# Кнопки
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛒 Посмотреть список"), KeyboardButton(text="📩 Отправить просьбу")],
        [KeyboardButton(text="🗑 Очистить всё")]
    ],
    resize_keyboard=True
)

# Веб-сервер для Render
async def handle(request):
    return aiohttp.web.Response(text="Bot is running")

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    users.add(message.from_user.id)
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
    user_states[message.from_user.id] = "waiting_for_request"
    await message.answer("Напиши текст просьбы, и я отправлю его другому человеку:")

@dp.message(F.text & ~F.text.startswith("/") & ~F.text.in_({"🛒 Посмотреть список", "🗑 Очистить всё", "📩 Отправить просьбу"}))
async def handle_text(message: types.Message):
    # Проверка: ждет ли бот сейчас просьбу от этого пользователя?
    if user_states.get(message.from_user.id) == "waiting_for_request":
        other_users = [u for u in users if u != message.from_user.id]
        if not other_users:
            await message.answer("Нет других пользователей, которым можно отправить просьбу.")
        else:
            for user_id in other_users:
                try:
                    await bot.send_message(user_id, f"🔔 Просьба от {message.from_user.first_name}:\n\n{message.text}")
                    await message.answer("✅ Отправлено!")
                except:
                    await message.answer("Не удалось отправить просьбу.")
        
        # Сбрасываем состояние
        user_states[message.from_user.id] = None
    else:
        # Если не ждем просьбу — значит, это товар в список
        shopping_list.append(message.text)
        await message.answer(f"✅ Добавлено в список покупок: {message.text}")

async def main():
    # Запуск веб-сервера (для Render)
    app = aiohttp.web.Application()
    app.router.add_get("/", handle)
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000))
    site = aiohttp.web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Сервер на порту {port} запущен!")
    
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
