import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command

BOT_TOKEN = "8783429061:AAHdivmiLwPts6u2cOUSRp_78RGf81PSP1w"
ADMIN_ID = 7518728008
ADMIN_USERNAME = "@support_usdt_rub"
WEBAPP_URL = "https://smswork34-art.github.io/p2p/index.html"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def keep_alive():
    while True:
        try:
            await bot.send_message(ADMIN_ID, "◇ Бот активен")
            await asyncio.sleep(600)
        except Exception:
            await asyncio.sleep(600)

@dp.message(Command("start"))
async def cmd_start(msg: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◆ Открыть обменник", web_app=WebAppInfo(url=WEBAPP_URL))],
        [
            InlineKeyboardButton(text="◎ Курс", callback_data="rate"),
            InlineKeyboardButton(text="◈ Поддержка", callback_data="support")
        ]
    ])
    await msg.answer(
        "<b>◆ USDT RUB Обменник</b>\n\n"
        "<i>Моментальный обмен USDT на RUB</i>\n\n"
        "<blockquote>Курс фиксируется при создании заявки\n"
        "Комиссия сервиса 0.5%\n"
        "Выплаты на карты СБП</blockquote>\n"
        "<b>◆ Для начала нажмите кнопку ниже.</b>",
        reply_markup=kb,
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "rate")
async def rate_callback(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer(
        "<b>◎ Актуальный курс</b>\n\n"
        "<i>Обмен от 63 USDT</i>\n\n"
        "<blockquote>80 RUB = 1 USDT\n"
        "Комиссия: 0.5%\n"
        "Минимальная сумма: 63 USDT</blockquote>\n"
        "<b>Курс фиксируется при создании заявки.</b>",
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "support")
async def support_callback(call: types.CallbackQuery):
    await call.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◈ Написать в поддержку", url=f"https://t.me/{ADMIN_USERNAME.lstrip('@')}")]
    ])
    await call.message.answer(
        "<b>◈ Поддержка</b>\n\n"
        "<i>По вопросам обмена и проверки транзакций</i>\n\n"
        "<blockquote>Возврат средств\n"
        "Время ответа: 5-15 минут</blockquote>\n"
        "<b>Для связи нажмите кнопку ниже.</b>",
        reply_markup=kb,
        parse_mode="HTML"
    )

@dp.message(Command("rate"))
async def rate_command(msg: types.Message):
    await msg.answer(
        "<b>◎ Курс: 80 RUB за 1 USDT</b>\n"
        "<i>Обмен от 63 USDT</i>\n\n"
        "<blockquote>Комиссия: 0.5%\n"
        "Минимум: 63 USDT</blockquote>",
        parse_mode="HTML"
    )

@dp.message(Command("support"))
async def support_command(msg: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◈ Поддержка", url=f"https://t.me/{ADMIN_USERNAME.lstrip('@')}")]
    ])
    await msg.answer("<b>Связь с поддержкой:</b>", reply_markup=kb, parse_mode="HTML")

@dp.message()
async def echo(msg: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◆ Открыть обменник", web_app=WebAppInfo(url=WEBAPP_URL))],
        [
            InlineKeyboardButton(text="◎ Курс", callback_data="rate"),
            InlineKeyboardButton(text="◈ Поддержка", callback_data="support")
        ]
    ])
    await msg.answer(
        "<b>◆ Используйте кнопки ниже для навигации.</b>",
        reply_markup=kb,
        parse_mode="HTML"
    )

async def main():
    asyncio.create_task(keep_alive())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
