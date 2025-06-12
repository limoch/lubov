import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
import logging
import os
from conf import TOKEN
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.types import BotCommand

choose = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="yes"),
            InlineKeyboardButton(text="Нет", callback_data="no")
        ]
    ]
)


# 📋 Настройка логирования
logging.basicConfig(level=logging.INFO)

# 🧠 Создание бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

users = []
authorizeusers = []
user_inputs = {}         # Храним статусы ввода
user_profiles = {}       # Храним анкеты (user_id: {имя})


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Начать"),
        BotCommand(command="setname", description="Заполнить анкету"),
        BotCommand(command="profile", description="Моя анкета"),
        BotCommand(command="profiles", description="Список всех анкет"),
    ]
    await bot.set_my_commands(commands)


# /start
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Привет! Давай создадим анкету.")

# /profile — регистрация (если не зарегистрирован)
@dp.message(Command("profile"))
async def profile_command(message: Message):
    user_id = message.from_user.id
    if user_id not in authorizeusers:
        await message.answer("О, я вижу ты тут впервые. Напиши /setname чтобы ввести имя.")
    else:
        name = user_profiles.get(user_id, {}).get("name", "Не указано")
        await message.answer(f"Ты уже зарегистрирован. Твоё имя: {name}")

# /setname — начинаем ввод имени
# Команда /setname
@dp.message(Command("setname"))
async def set_name(message: Message):
    user_id = message.from_user.id
    if user_id not in authorizeusers:
        user_inputs[user_id] = "waiting_for_name"
        await message.answer("Введи своё имя:")
    else:
        await message.answer(
            "Ты уже зарегистрирован. Хочешь заполнить заново?",
            reply_markup=choose)

# Обработка нажатий по кнопкам
@dp.callback_query()
async def handle_re_register(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    action = callback.dataы

    if action == "yes":
        if user_id in users:
            users.remove(user_id)
        if user_id in authorizeusers:
            authorizeusers.remove(user_id)
        user_inputs[user_id] = "waiting_for_name"
        await callback.message.answer("Солнышко, твои данные очищены. Введи своё имя:")
    elif action == "no":
        await callback.message.answer("Хорошо, оставим как есть 😊")

    await callback.answer()




# /profiles — отладка: список пользователей
@dp.message(Command("profiles"))
async def profiles_command(message: Message):
    await message.answer(f"ID всех пользователей: {users}\nЗарегистрированные: {authorizeusers}")

# Обработка любого текста (если ждём имя)
@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    text = message.text

    if user_inputs.get(user_id) == "waiting_for_name":
        # Сохраняем имя
        user_profiles[user_id] = {"name": text}
        authorizeusers.append(user_id)
        users.append(user_id)

        user_inputs[user_id] = None  # сбрасываем ожидание
        await message.answer(f"Имя сохранено! Добро пожаловать, {text}")
    else:
        await message.answer("Не понял тебя. Напиши /setname чтобы задать имя.")

# 🚀 Запуск бота
async def main():
    print("Бот запущен...")
    await set_commands(bot)  # ← Установка команд в Telegr
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
