import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command

BOT_TOKEN = os.getenv("BOT_TOKEN", "8783429061:AAHdivmiLwPts6u2cOUSRp_78RGf81PSP1w")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "@support_usdt_rub")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://твой-сайт.com/index.html")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(msg: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◈ Открыть обменник", web_app=WebAppInfo(url=WEBAPP_URL))],
        [
            InlineKeyboardButton(text="♟ Курс", callback_data="rate"),
            InlineKeyboardButton(text="♛ Поддержка", callback_data="support")
        ]
    ])
    await msg.answer(
        "◈ USDT RUB Обменник\n\n"
        "◇ Моментальный обмен USDT на RUB\n"
        "◇ Курс фиксируется при создании заявки\n"
        "◇ Комиссия сервиса 0.5%\n"
        "◇ Выплаты на карты СБП\n\n"
        "◈ Для начала нажмите кнопку ниже.",
        reply_markup=kb
    )

@dp.callback_query(F.data == "rate")
async def rate_callback(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer(
        "♟ Актуальный курс\n\n"
        "◇ 72 RUB = 1 USDT\n"
        "◇ Комиссия: 0.5%\n"
        "◇ Минимальная сумма: 10 USDT\n\n"
        "Курс фиксируется при создании заявки."
    )

@dp.callback_query(F.data == "support")
async def support_callback(call: types.CallbackQuery):
    await call.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="♛ Написать в поддержку", url=f"https://t.me/{ADMIN_USERNAME.lstrip('@')}")]
    ])
    await call.message.answer(
        "♛ Поддержка\n\n"
        "◇ По вопросам обмена и проверки транзакций\n"
        "◇ Возврат средств\n"
        "◇ Время ответа: 5-15 минут\n\n"
        "Для связи нажмите кнопку ниже.",
        reply_markup=kb
    )

@dp.message(Command("rate"))
async def rate_command(msg: types.Message):
    await msg.answer(
        "♟ Курс: 72 RUB за 1 USDT\n"
        "◇ Комиссия: 0.5%\n"
        "◇ Минимум: 10 USDT"
    )

@dp.message(Command("support"))
async def support_command(msg: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="♛ Поддержка", url=f"https://t.me/{ADMIN_USERNAME.lstrip('@')}")]
    ])
    await msg.answer("Связь с поддержкой:", reply_markup=kb)

@dp.message()
async def echo(msg: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◈ Открыть обменник", web_app=WebAppInfo(url=WEBAPP_URL))],
        [
            InlineKeyboardButton(text="♟ Курс", callback_data="rate"),
            InlineKeyboardButton(text="♛ Поддержка", callback_data="support")
        ]
    ])
    await msg.answer(
        "◈ Используйте кнопки ниже для навигации.",
        reply_markup=kb
    )

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
