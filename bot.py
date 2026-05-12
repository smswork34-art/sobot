import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.filters import Command

BOT_TOKEN = os.getenv("BOT_TOKEN", "8783429061:AAHdivmiLwPts6u2cOUSRp_78RGf81PSP1w")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "@support_usdt_rub")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://твой-сайт.com/index.html")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(msg: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Обмен USDT на RUB", web_app=WebAppInfo(url=WEBAPP_URL))],
            [KeyboardButton(text="Поддержка"), KeyboardButton(text="Курс")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )
    await msg.answer(
        "USDT на RUB — быстрый обмен.\n\n"
        "Нажмите кнопку ниже для создания заявки.\n"
        "Курс фиксируется на момент создания.",
        reply_markup=kb
    )

@dp.message(F.text == "Обмен USDT на RUB")
async def exchange_btn(msg: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Создать заявку",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])
    await msg.answer("Нажмите кнопку для перехода в обменник.", reply_markup=kb)

@dp.message(F.text == "Курс")
async def rate_cmd(msg: types.Message):
    await msg.answer(
        "Курс: 72 RUB за 1 USDT\n"
        "Комиссия: 0.5%\n"
        "Минимум: 10 USDT\n\n"
        "Курс фиксируется при создании заявки."
    )

@dp.message(F.text == "Поддержка")
async def support_cmd(msg: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Написать в поддержку",
            url=f"https://t.me/{ADMIN_USERNAME.lstrip('@')}"
        )]
    ])
    await msg.answer(
        "По вопросам обмена и проверки транзакций обращайтесь в поддержку.\n"
        "Время ответа: 5-15 минут.",
        reply_markup=kb
    )

@dp.message(Command("support"))
async def support_command(msg: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Поддержка",
            url=f"https://t.me/{ADMIN_USERNAME.lstrip('@')}"
        )]
    ])
    await msg.answer("Связь с поддержкой:", reply_markup=kb)

@dp.message(Command("rate"))
async def rate_command(msg: types.Message):
    await msg.answer("Курс: 72 RUB за 1 USDT\nКомиссия: 0.5%\nМинимум: 10 USDT")

@dp.message()
async def echo(msg: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Обмен USDT на RUB", web_app=WebAppInfo(url=WEBAPP_URL))],
            [KeyboardButton(text="Поддержка"), KeyboardButton(text="Курс")]
        ],
        resize_keyboard=True
    )
    await msg.answer("Используйте кнопки ниже.", reply_markup=kb)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
