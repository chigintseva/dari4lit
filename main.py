import asyncio
import os
import aiohttp.web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

shopping_list = []
users = set()
# Состояния: None, "waiting_for_product", "waiting_for_request"
user_states = {}

# Кнопки
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить продукт"), KeyboardButton(text="🛒 Посмотреть список")],
        [KeyboardButton(text="📩 Отправить просьбу"), KeyboardButton(text="🗑 Очистить всё")]
    ],
    resize_keyboard=True
)

async def handle(request):
    return aiohttp.web.Response(text="Bot is running")

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    users.add(message.from_user.id)
    await message.answer("Привет! Я твой семейный помощник.", reply_markup=keyboard)

@dp.message(F.text == "➕ Добавить продукт")
async def ask_product(message: types.Message):
    user_states[message.from_user.id] = "waiting_for_product"
    await message.answer("Напиши название продукта, который нужно добавить:")

@dp.message(F.text == "📩 Отправить просьбу")
async def ask_request(message: types.Message):
    user_states[message.from_user.id] = "waiting_for_request"
    await message.answer("Напиши текст просьбы:")

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
    await message.answer("Список очищен!")

@dp.message(F.text & ~F.text.startswith("/"))
async def handle_text(message: types.Message):
    state = user_states.get(message.from_user.id)
    
    if state == "waiting_for_product":
        shopping_list.append(message.text)
        await message.answer(f"✅ {message.text} добавлено в список!")
        user_states[message.from_user.id] = None
        
    elif state == "waiting_for_request":
        other_users = [u for u in users if u != message.from_user.id]
        if not other_users:
            await message.answer("Нет других пользователей.")
        else:
            for user_id in other_users:
                await bot.send_message(user_id, f"🔔 Просьба от {message.from_user.first_name}:\n\n{message.text}")
            await message.answer("✅ Отправлено!")
        user_states[message.from_user.id] = None
        
    else:
        await message.answer("Используй кнопки для выбора действия.", reply_markup=keyboard)

async def main():
    app = aiohttp.web.Application()
    app.router.add_get("/", handle)
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = aiohttp.web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
