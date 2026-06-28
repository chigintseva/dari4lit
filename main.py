import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Наш список покупок
shopping_list = []

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привет! Я твой бот-помощник.\n"
                         "Пиши название продукта, чтобы добавить его в список.\n"
                         "Команды: /list — посмотреть список, /clear — очистить.")

@dp.message(Command("list"))
async def show_list(message: types.Message):
    if not shopping_list:
        await message.answer("Список покупок пуст!")
    else:
        text = "🛒 **Список покупок:**\n\n" + "\n".join([f"• {item}" for item in shopping_list])
        await message.answer(text, parse_mode="Markdown")

@dp.message(Command("clear"))
async def clear_list(message: types.Message):
    shopping_list.clear()
    await message.answer("Список очищен!")

# Добавление продукта (все, что не команда)
@dp.message(F.text & ~F.text.startswith("/"))
async def add_item(message: types.Message):
    item = message.text.strip()
    shopping_list.append(item)
    await message.answer(f"✅ Добавила '{item}' в список!")
    
    # "Уведомление": кидаем сообщение в ответ
    # Можно сделать так, чтобы бот сам напоминал, если нужно
    await message.answer(f"Не забудь купить: {item}!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
