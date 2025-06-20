import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    BotCommand,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)
from conf import TOKEN
from db import init_db, save_user, get_user, get_all_users, delete_user
from keyboards import choose, gender, lovechoose, mainmenu
import random

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранилище состояний
user_inputs = {}
temp_profiles = {}
viewed_profiles = {}  # user_id: [user_ids которые уже видел]


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="setname", description="Заполнить анкету"),
        BotCommand(command="profile", description="Моя анкета"),
        BotCommand(command="profiles", description="Список всех анкет"),
    ]
    await bot.set_my_commands(commands)


async def send_profile(user_id, chat_id):
    user = await get_user(user_id)
    if user:
        name, age, gender, interests, photo_id = user
        caption = f"🧾 Твоя анкета:\nИмя: {name}\nВозраст: {age}\nПол: {gender}\nИнтересы: {interests}"
        await bot.send_photo(chat_id=chat_id, photo=photo_id, caption=caption)
    else:
        await bot.send_message(chat_id, "Ты ещё не создавал анкету. Хочешь создать? 😊", reply_markup=choose)


async def sendrandom_profile(user_id, chat_id):
    all_users = await get_all_users()

    # Все другие анкеты кроме своей
    other_users = [user for user in all_users if str(user[0]) != str(user_id)]

    if not other_users:
        await bot.send_message(chat_id, "Пока нет других анкет 😔")
        return

    # Получаем список id, которые пользователь уже видел
    seen = viewed_profiles.get(user_id, [])

    # Фильтруем ещё не просмотренные анкеты
    unseen_users = [user for user in other_users if user[0] not in seen]

    if not unseen_users:
        # Если все просмотрены — сбрасываем
        viewed_profiles[user_id] = []
        await bot.send_message(chat_id, "Ты посмотрел все анкеты. Начинаем заново 🔁")
        unseen_users = other_users

    # Выбираем случайную анкету из непросмотренных
    random_user = random.choice(unseen_users)
    viewed_profiles.setdefault(user_id, []).append(random_user[0])  # сохраняем как просмотренную

    _, name, age, gender, interests, photo_id = random_user
    caption = f"💘 Случайная анкета:\nИмя: {name}\nВозраст: {age}\nПол: {gender}\nИнтересы: {interests}"
    await bot.send_photo(chat_id=chat_id, photo=photo_id, caption=caption, reply_markup=lovechoose)


@dp.message(Command("start"))
async def start_command(message: Message):
    user_id = message.from_user.id
    profile = await get_user(user_id)
    if not profile:
        user_inputs[user_id] = "name"
        temp_profiles[user_id] = {}
        await message.answer("Привет!", reply_markup=mainmenu)
    else:
        await message.answer("Ты уже зарегистрирован. Хочешь заполнить заново?", reply_markup=choose)


@dp.message(Command("setname"))
async def set_name(message: Message):
    user_id = message.from_user.id
    profile = await get_user(user_id)
    if not profile:
        user_inputs[user_id] = "name"
        temp_profiles[user_id] = {}
        await message.answer("Как тебя зовут?")
    else:
        await message.answer("Ты уже зарегистрирован. Хочешь заполнить заново?", reply_markup=choose)


@dp.message(Command("profile"))
async def show_profile(message: Message):
    await send_profile(message.from_user.id, message.chat.id)


@dp.message(Command("profiles"))
async def profiles_command(message: Message):
    all_users = await get_all_users()
    if not all_users:
        await message.answer("Пока нет анкет.")
        return

    text = "\n\n".join([
        f"ID: {uid}\nИмя: {name}\nВозраст: {age}\nПол: {gender}\nИнтересы: {interests}\nФото: {photo_id}"
        for uid, name, age, gender, interests, photo_id in all_users
    ])
    await message.answer(text)


@dp.callback_query()
async def handle_re_register(callback: CallbackQuery):
    user_id = callback.from_user.id
    action = callback.data

    if action == "yes":
        await delete_user(user_id)
        user_inputs[user_id] = "name"
        temp_profiles[user_id] = {}
        await callback.message.answer("Отлично. Введи имя:")
    elif action == "no":
        await callback.message.answer("Хорошо, оставим как есть 😊", reply_markup=mainmenu)
    elif action == "like":
        await callback.message.answer("Отлично. Введи имя:")

    await callback.answer()


@dp.message(lambda message: message.photo)
async def handle_photo(message: Message):
    user_id = message.from_user.id
    step = user_inputs.get(user_id)

    if step == "photo_id":
        photo = message.photo[-1]
        file_id = photo.file_id

        temp_profiles[user_id]["photo_id"] = file_id
        data = temp_profiles.pop(user_id)
        user_inputs.pop(user_id)

        await save_user(
            user_id=user_id,
            name=data["name"],
            age=data["age"],
            gender=data["gender"],
            interests=data["interests"],
            photo_id=data["photo_id"]
        )

        await message.answer("Анкета успешно сохранена, спасибо!", reply_markup=mainmenu)
    else:
        await message.answer("Сейчас фото не требуется.")


@dp.message()
async def handle_input(message: Message):
    if not message.text:
        return

    text = message.text.strip()
    user_id = message.from_user.id
    chat_id = message.chat.id
    step = user_inputs.get(user_id)

    # Обработка шагов анкеты
    if step == "name":
        temp_profiles[user_id] = {"name": text}
        user_inputs[user_id] = "age"
        await message.answer("Сколько тебе лет?")

    elif step == "age":
        if text.isdigit():
            temp_profiles[user_id]["age"] = int(text)
            user_inputs[user_id] = "gender"
            await message.answer("Твой пол?", reply_markup=gender)
        else:
            await message.answer("Пожалуйста, введи число.")

    elif step == "gender":
        if text in ["Парень", "Девушка"]:
            temp_profiles[user_id]["gender"] = text
            user_inputs[user_id] = "interests"
            await message.answer("Придумай классное описание", reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer("Пожалуйста, выбери пол, используя кнопки ниже.", reply_markup=gender)

    elif step == "interests":
        temp_profiles[user_id]["interests"] = text
        user_inputs[user_id] = "photo_id"
        await message.answer("Пришли фотку на аву 📸")

    # Обработка кнопки "Профиль"
    elif text.lower() == "профиль":
        user_id = message.from_user.id
        profile = await get_user(user_id)
        if not profile:
            await bot.send_message(chat_id, "Ты ещё не создавал анкету. Хочешь создать? 😊", reply_markup=choose)
        else:
            await send_profile(user_id, chat_id)

    elif text.lower() == "лента":
        await sendrandom_profile(message.from_user.id, message.chat.id)
        

    else:
        await message.answer("Напиши /setname чтобы заполнить анкету.")


async def main():
    print("Запуск бота...")
    await init_db()
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())