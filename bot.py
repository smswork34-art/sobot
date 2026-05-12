import asyncio
import os
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, FSInputFile
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

BOT_TOKEN = "8783429061:AAHdivmiLwPts6u2cOUSRp_78RGf81PSP1w"
ADMIN_USERNAME = "@support_usdt_rub"
WEBAPP_URL = "https://smswork34-art.github.io/p2p/index.html"
ADMIN_PANEL_URL = "https://smswork34-art.github.io/admin/index.html"
RENDER_URL = "https://lvk-bot.onrender.com"
PORT = int(os.getenv("PORT", 10000))

ADMIN_ID = 7518728008
ADMINS = [7518728008]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def init_db():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            role TEXT DEFAULT 'user',
            created_at TEXT,
            last_active TEXT,
            blocked INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def save_user(user: types.User):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO users (id, username, first_name, role, created_at, last_active)
        VALUES (?, ?, ?,
            COALESCE((SELECT role FROM users WHERE id = ?), 'user'),
            COALESCE((SELECT created_at FROM users WHERE id = ?), ?),
            ?
        )
    """, (user.id, user.username, user.first_name, user.id, user.id, datetime.utcnow().isoformat(), datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users ORDER BY last_active DESC")
    users = c.fetchall()
    conn.close()
    return users

def get_user_count():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    conn.close()
    return count

def is_admin(user_id):
    return user_id in ADMINS

@dp.message(Command("start"))
async def cmd_start(msg: types.Message):
    save_user(msg.from_user)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◆ Открыть обменник", web_app=WebAppInfo(url=WEBAPP_URL))],
        [
            InlineKeyboardButton(text="◎ Курс", callback_data="rate", style="primary"),
            InlineKeyboardButton(text="◈ Поддержка", callback_data="support", style="primary")
        ]
    ])
    if is_admin(msg.from_user.id):
        kb.inline_keyboard.append([
            InlineKeyboardButton(text="◆ Админ-панель", web_app=WebAppInfo(url=ADMIN_PANEL_URL))
        ])
    try:
        photo = FSInputFile("banner.jpg")
        await msg.answer_photo(
            photo,
            caption=(
                "<b>◆ USDT RUB Обменник</b>\n\n"
                "<i>Моментальный обмен USDT на RUB</i>\n\n"
                "<blockquote>Курс фиксируется при создании заявки\n"
                "Комиссия сервиса 0.5%\n"
                "Выплаты на карты СБП</blockquote>\n"
                "<b>◆ Для начала нажмите кнопку ниже.</b>"
            ),
            reply_markup=kb,
            parse_mode="HTML"
        )
    except Exception:
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
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◆ Открыть обменник", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="◈ В главное меню", callback_data="back_to_main", style="primary")]
    ])
    await call.message.answer(
        "<b>◎ Актуальный курс</b>\n\n"
        "<i>Обмен от 63 USDT</i>\n\n"
        "<blockquote>80 RUB = 1 USDT\n"
        "Комиссия: 0.5%\n"
        "Минимальная сумма: 63 USDT</blockquote>\n"
        "<b>Курс фиксируется при создании заявки.</b>",
        reply_markup=kb,
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "support")
async def support_callback(call: types.CallbackQuery):
    await call.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◈ В главное меню", callback_data="back_to_main", style="primary")]
    ])
    await call.message.answer(
        "<b>◈ Поддержка</b>\n\n"
        "<i>Чтобы создать тикет, введите команду:</i>\n"
        "<code>/ticket ваш вопрос</code>\n\n"
        "<blockquote>Пример:\n"
        "/ticket Не пришли деньги после оплаты</blockquote>\n"
        "<b>Время ответа: 5-15 минут.</b>",
        reply_markup=kb,
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "admin_stats")
async def admin_stats_callback(call: types.CallbackQuery):
    await call.answer()
    count = get_user_count()
    await call.message.answer(f"<b>◆ Статистика</b>\n\nВсего пользователей: <b>{count}</b>", parse_mode="HTML")

@dp.callback_query(F.data == "back_to_main")
async def back_to_main_callback(call: types.CallbackQuery):
    await call.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◆ Открыть обменник", web_app=WebAppInfo(url=WEBAPP_URL))],
        [
            InlineKeyboardButton(text="◎ Курс", callback_data="rate", style="primary"),
            InlineKeyboardButton(text="◈ Поддержка", callback_data="support", style="primary")
        ]
    ])
    if is_admin(call.from_user.id):
        kb.inline_keyboard.append([
            InlineKeyboardButton(text="◆ Админ-панель", web_app=WebAppInfo(url=ADMIN_PANEL_URL))
        ])
    await call.message.answer("<b>◆ Главное меню</b>", reply_markup=kb, parse_mode="HTML")

@dp.message(Command("ticket"))
async def ticket_command(msg: types.Message):
    save_user(msg.from_user)
    text = msg.text.replace("/ticket", "").strip()
    if not text:
        await msg.answer(
            "<b>◇ Укажите вопрос после команды.</b>\n"
            "<i>Пример:</i> <code>/ticket Не пришли деньги</code>",
            parse_mode="HTML"
        )
        return

    user_info = f"@{msg.from_user.username}" if msg.from_user.username else f"ID: {msg.from_user.id}"
    admin_text = (
        f"<b>◇ Новый тикет</b>\n"
        f"<b>От:</b> {user_info}\n"
        f"<code>{text}</code>"
    )
    await bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML")
    await msg.answer(
        "<b>◇ Тикет открыт</b>\n"
        "<i>Ваш вопрос отправлен. Ожидайте ответа.</i>\n\n"
        "Для закрытия тикета: /close",
        parse_mode="HTML"
    )

@dp.message(Command("close"))
async def close_command(msg: types.Message):
    await msg.answer("<b>◇ Тикет закрыт.</b>", parse_mode="HTML")

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
    await msg.answer(
        "<b>◈ Поддержка</b>\n\n"
        "<i>Чтобы создать тикет, введите:</i>\n"
        "<code>/ticket ваш вопрос</code>",
        parse_mode="HTML"
    )

@dp.message(Command("stats"))
async def stats_command(msg: types.Message):
    if not is_admin(msg.from_user.id):
        return
    count = get_user_count()
    await msg.answer(f"<b>◆ Статистика</b>\n\nВсего пользователей: <b>{count}</b>", parse_mode="HTML")

@dp.message(Command("broadcast"))
async def broadcast_command(msg: types.Message):
    if not is_admin(msg.from_user.id):
        return
    text = msg.text.replace("/broadcast", "").strip()
    if not text:
        await msg.answer("◆ Укажите текст.\nПример: <code>/broadcast Всем привет!</code>", parse_mode="HTML")
        return
    users = get_all_users()
    success = 0
    for u in users:
        try:
            await bot.send_message(u[0], text)
            success += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
    await msg.answer(f"<b>◆ Рассылка завершена</b>\nОтправлено: {success}", parse_mode="HTML")

@dp.message(Command("admin"))
async def admin_command(msg: types.Message):
    if not is_admin(msg.from_user.id):
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◆ Админ-панель", web_app=WebAppInfo(url=ADMIN_PANEL_URL))],
        [InlineKeyboardButton(text="◆ Статистика", callback_data="admin_stats", style="primary")]
    ])
    await msg.answer("<b>◆ Админ-меню</b>", reply_markup=kb, parse_mode="HTML")

@dp.message(F.text)
async def handle_message(msg: types.Message):
    save_user(msg.from_user)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◆ Открыть обменник", web_app=WebAppInfo(url=WEBAPP_URL))],
        [
            InlineKeyboardButton(text="◎ Курс", callback_data="rate", style="primary"),
            InlineKeyboardButton(text="◈ Поддержка", callback_data="support", style="primary")
        ]
    ])
    if is_admin(msg.from_user.id):
        kb.inline_keyboard.append([
            InlineKeyboardButton(text="◆ Админ-панель", web_app=WebAppInfo(url=ADMIN_PANEL_URL))
        ])
    await msg.answer("<b>◆ Используйте кнопки ниже.</b>", reply_markup=kb, parse_mode="HTML")

@dp.message(F.reply_to_message)
async def handle_reply(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return
    if not msg.reply_to_message or not msg.reply_to_message.text:
        return
    text = msg.reply_to_message.text
    for line in text.split("\n"):
        if "ID:" in line:
            try:
                user_id = int(line.split("ID:")[1].strip())
                await bot.send_message(
                    user_id,
                    f"<b>◇ Ответ поддержки:</b>\n<code>{msg.text}</code>",
                    parse_mode="HTML"
                )
                await msg.answer("<b>◇ Ответ отправлен.</b>", parse_mode="HTML")
                return
            except Exception:
                pass
    await msg.answer("<b>◇ Не удалось определить пользователя.</b>", parse_mode="HTML")

async def on_startup():
    init_db()
    await bot.set_webhook(f"{RENDER_URL}/webhook")

async def main():
    await on_startup()
    app = web.Application()
    handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    handler.register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
