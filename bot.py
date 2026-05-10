# bot.py — ДЛЯ RENDER.COM
import asyncio
import json
import os
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# --- НАСТРОЙКИ ---
BOT_TOKEN = ("8764168047:AAGA3G3z8gjOwFVpcUBKBzEvME4FCntRvSs")  # Токен из переменных окружения
ADMIN_IDS = [123456789]             # Твой Telegram ID
WEBAPP_URL = "https://smswork34-art.github.io/jangel/index.html"  # GitHub Pages или другой хостинг HTML
USERS_FILE = "users.json"
RENDER_URL = ("https://lvk-bot.onrender.comL", "")  # Render сам даст URL

# --- ЛОГИРОВАНИЕ ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- БАЗА ПОЛЬЗОВАТЕЛЕЙ ---
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def add_user(user: types.User):
    users = load_users()
    uid = str(user.id)
    if uid not in users:
        users[uid] = {
            "id": user.id,
            "first_name": user.first_name,
            "username": user.username,
            "joined_at": datetime.now().strftime("%d.%m.%Y %H:%M")
        }
        save_users(users)

def get_all_users():
    return load_users()

def get_users_count():
    return len(load_users())

# --- БОТ ---
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# --- КЛАВИАТУРЫ ---
def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Открыть LVK Service", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="💬 Поддержка", url="https://t.me/LVKSupport")],
        [InlineKeyboardButton(text="🛡 Гарант", url="https://t.me/Sponge_05")]
    ])

def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📨 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users")],
        [InlineKeyboardButton(text="🔙 Выйти", callback_data="admin_exit")]
    ])

# --- FSM ---
class BroadcastState(StatesGroup):
    waiting_for_message = State()

# --- ОБРАБОТЧИКИ ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    add_user(message.from_user)
    await message.answer(
        "👋 <b>Добро пожаловать в LVK Service!</b>\n\n"
        "Здесь вы можете просматривать объявления, публиковать свои услуги "
        "и общаться с другими пользователями.\n\n"
        "Нажмите кнопку ниже, чтобы открыть сервис 👇",
        reply_markup=main_keyboard()
    )

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("🔐 <b>Админ-панель</b>\nВыберите действие:", reply_markup=admin_keyboard())
    else:
        await message.answer("⛔ У вас нет доступа.")

@dp.callback_query(F.data == "admin_exit")
async def admin_exit(callback: types.CallbackQuery):
    await callback.message.edit_text("👋 <b>LVK Service</b>\n\nНажмите кнопку, чтобы открыть сервис 👇", reply_markup=main_keyboard())
    await callback.answer("Вы вышли из админ-панели")

@dp.callback_query(F.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    count = get_users_count()
    await callback.message.edit_text(
        f"📊 <b>Статистика бота</b>\n\n👥 Всего пользователей: <b>{count}</b>\n📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")]])
    )
    await callback.answer()

@dp.callback_query(F.data == "admin_users")
async def admin_users(callback: types.CallbackQuery):
    users = get_all_users()
    if not users:
        text = "👥 Пользователей пока нет."
    else:
        text = f"👥 <b>Пользователи ({len(users)})</b>\n\n"
        for uid, data in list(users.items())[-10:]:
            username = f"@{data['username']}" if data.get('username') else "без username"
            text += f"• <b>{data['first_name']}</b> {username} — {data['joined_at']}\n"
        if len(users) > 10:
            text += f"\n<i>Показаны последние 10 из {len(users)}</i>"
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")]]))
    await callback.answer()

@dp.callback_query(F.data == "admin_back")
async def admin_back(callback: types.CallbackQuery):
    await callback.message.edit_text("🔐 <b>Админ-панель</b>\nВыберите действие:", reply_markup=admin_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📨 <b>Рассылка</b>\n\nОтправьте сообщение для всех пользователей.\nДля отмены — /cancel",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Отмена", callback_data="admin_back")]])
    )
    await state.set_state(BroadcastState.waiting_for_message)
    await callback.answer()

@dp.message(BroadcastState.waiting_for_message)
async def broadcast_send(message: types.Message, state: FSMContext):
    if message.text and message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Рассылка отменена.", reply_markup=admin_keyboard())
        return
    users = get_all_users()
    success = 0
    fail = 0
    await message.answer(f"📨 Рассылаю на {len(users)} пользователей...")
    for uid in users:
        try:
            await bot.copy_message(chat_id=int(uid), from_chat_id=message.chat.id, message_id=message.message_id)
            success += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            fail += 1
            logger.error(f"Ошибка {uid}: {e}")
    await message.answer(f"✅ <b>Готово!</b>\n✓ Успешно: {success}\n✗ Ошибок: {fail}", reply_markup=admin_keyboard())
    await state.clear()

# --- ЗАПУСК (WEBHOOK ДЛЯ RENDER) ---
async def on_startup(bot: Bot):
    await bot.set_webhook(f"{RENDER_URL}/webhook")
    logger.info(f"Webhook установлен: {RENDER_URL}/webhook")

async def main():
    dp.startup.register(on_startup)
    app = web.Application()
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    logger.info("Бот запущен!")
    return app

if __name__ == "__main__":
    app = asyncio.run(main())
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
