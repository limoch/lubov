import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
import logging
import os
from conf import TOKEN
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, BotCommand
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

choose = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="yes"),
            InlineKeyboardButton(text="Нет", callback_data="no")
        ]
    ]
)

lovechoose = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Лайк", callback_data="like"),
            InlineKeyboardButton(text="Скип", callback_data="skip"),
            InlineKeyboardButton(text="Задонатить", callback_data="donate")
        ]
    ]
)

gender = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Парень", callback_data="men"), 
         KeyboardButton(text="Девушка", callback_data="women")]
    ],
    resize_keyboard=True,  # подгоняет по размеру экрана
    one_time_keyboard=True  # скрывается после нажатия
)

# Главное меню с кнопками (ReplyKeyboard)
mainmenu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Профиль"),
            KeyboardButton(text="Лайки"),
            KeyboardButton(text="Лента"),
            KeyboardButton(text="Поддержать")
        ]
    ],
    resize_keyboard=True
)

