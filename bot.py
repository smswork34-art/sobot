import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, WEBAPP_URL
import logging

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💳 Открыть платежный шлюз",
            web_app=WebAppInfo(url=f"{WEBAPP_URL}")
        )],
        [InlineKeyboardButton(
            text="📊 Мои платежи",
            callback_data="my_payments"
        )],
        [InlineKeyboardButton(
            text="ℹ️ Помощь",
            callback_data="help"
        )]
    ])
    
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я помогу тебе совершать крипто-платежи.\n"
        "Выбери действие:",
        reply_markup=keyboard
    )

@dp.message(Command("pay"))
async def cmd_pay(message: types.Message):
    """Команда для создания платежа"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💰 Создать платеж",
            web_app=WebAppInfo(url=f"{WEBAPP_URL}/create")
        )]
    ])
    
    await message.answer(
        "Выбери сумму для оплаты:",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data == "my_payments")
async def process_my_payments(callback: types.CallbackQuery):
    await callback.message.answer(
        "📊 Здесь будет история твоих платежей"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "help")
async def process_help(callback: types.CallbackQuery):
    await callback.message.answer(
        "ℹ️ Помощь\n\n"
        "Для создания платежа используй команду /pay\n"
        "Поддерживаемые валюты: USDT, BTC, ETH\n"
        "Минимальная сумма: 10 USDT"
    )
    await callback.answer()

async def main():
    await dp.start_polling(bot)

def start_bot():
    """Запуск бота"""
    logging.info("Starting Telegram bot...")
    asyncio.run(main())

if __name__ == '__main__':
    start_bot()
