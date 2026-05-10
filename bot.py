# bot.py — POLLING VERSION (RENDER.COM)
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

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8764168047:AAGA3G3z8gjOwFVpcUBKBzEvME4FCntRvSs"
ADMIN_IDS = [7518728008]
WEBAPP_URL = "https://smswork34-art.github.io/jangel//index.html"
USERS_FILE = "users.json"

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
        logger.info(f"Новый пользователь: {user.first_name} (ID: {user.id})")

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
        [InlineKeyboardButton(
            text="🚀 ОТКРЫТЬ LVK SERVICE",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )],
        [InlineKeyboardButton(
            text="💬 Поддержка",
            callback_data="support_info"
        )],
        [InlineKeyboardButton(
            text="🛡 Гарант",
            callback_data="garant_info"
        )]
    ])
    
def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📨 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users")],
        [InlineKeyboardButton(text="🔙 Выйти", callback_data="admin_exit")]
    ])

# --- FSM ДЛЯ РАССЫЛКИ ---
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

# --- CALLBACKS: ПОДДЕРЖКА И ГАРАНТ ---

@dp.callback_query(F.data == "support_info")
async def support_info(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Написать в поддержку", url="https://t.me/LVKSupport")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ])
    await callback.message.edit_text(
        "💬 <b>Поддержка LVK Service</b>\n\n"
        "Если у вас возникли вопросы, проблемы с работой сервиса "
        "или требуется помощь — нажмите кнопку ниже, чтобы связаться с нами.\n\n"
        "Мы обязательно поможем! 🫡",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "garant_info")
async def garant_info(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛡 Связаться с гарантом", url="https://t.me/Sponge_05")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ])
    await callback.message.edit_text(
        "🛡 <b>Гарант сделок — СПАНЧ</b>\n\n"
        "Гарант обеспечивает безопасное проведение сделок с использованием USDT.\n\n"
        "Как это работает:\n"
        "• Покупатель переводит средства гаранту\n"
        "• Продавец передаёт товар/услугу\n"
        "• Гарант переводит средства продавцу\n\n"
        "Сделка проходит безопасно для обеих сторон. "
        "Нажмите кнопку ниже, чтобы связаться с гарантом.",
        reply_markup=keyboard
    )
    await callback.answer()

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "👋 <b>LVK Service</b>\n\nНажмите кнопку, чтобы открыть сервис 👇",
        reply_markup=main_keyboard()
    )
    await callback.answer()

# --- CALLBACKS: АДМИНКА ---

@dp.callback_query(F.data == "admin_exit")
async def admin_exit(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "👋 <b>LVK Service</b>\n\nНажмите кнопку, чтобы открыть сервис 👇",
        reply_markup=main_keyboard()
    )
    await callback.answer("Вы вышли из админ-панели")

@dp.callback_query(F.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    count = get_users_count()
    await callback.message.edit_text(
        f"📊 <b>Статистика бота</b>\n\n"
        f"👥 Всего пользователей: <b>{count}</b>\n"
        f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")]
        ])
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
            text += f"• <b>{data['first_name']}</b> {username} — ID: <code>{data['id']}</code>\n"
        if len(users) > 10:
            text += f"\n<i>Показаны последние 10 из {len(users)}</i>"

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "admin_back")
async def admin_back(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🔐 <b>Админ-панель</b>\nВыберите действие:",
        reply_markup=admin_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📨 <b>Рассылка</b>\n\n"
        "Отправьте сообщение, которое будет разослано всем пользователям.\n"
        "Для отмены отправьте /cancel",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="admin_back")]
        ])
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

    await message.answer(f"📨 Начинаю рассылку на {len(users)} пользователей...")

    for uid in users:
        try:
            await bot.copy_message(
                chat_id=int(uid),
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
            success += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            fail += 1
            logger.error(f"Ошибка отправки {uid}: {e}")

    await message.answer(
        f"✅ <b>Рассылка завершена!</b>\n\n"
        f"✓ Успешно: {success}\n"
        f"✗ Ошибок: {fail}",
        reply_markup=admin_keyboard()
    )
    await state.clear()

# --- КОМАНДЫ ДЛЯ ГРУППЫ ---

@dp.message(Command("ban"))
async def cmd_ban(message: types.Message):
    # Проверяем, что команда в группе
    if message.chat.type == "private":
        await message.answer("⛔ Эта команда работает только в группе.")
        return

    # Проверяем, что пользователь — админ группы или владелец
    user_id = message.from_user.id
    chat_id = message.chat.id
    sender = await bot.get_chat_member(chat_id, user_id)
    
    if sender.status not in ["creator", "administrator"]:
        await message.answer("⛔ У вас нет прав для использования этой команды.")
        return

    # Проверяем, что бот — админ с правом бана
    bot_member = await bot.get_chat_member(chat_id, bot.id)
    if not bot_member.can_restrict_members:
        await message.answer("⛔ Бот не имеет прав для блокировки пользователей.")
        return

    # Получаем цель: /ban @username или /ban в ответ на сообщение
    target = None

    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif message.text and len(message.text.split()) > 1:
        username = message.text.split()[1].replace("@", "")
        try:
            target = await bot.get_chat_member(chat_id, username)
            target = target.user
        except:
            await message.answer("❌ Пользователь не найден.")
            return
    else:
        await message.answer("ℹ️ Использование: /ban @username или ответьте на сообщение пользователя.")
        return

    # Нельзя забанить админа или владельца
    target_member = await bot.get_chat_member(chat_id, target.id)
    if target_member.status in ["creator", "administrator"]:
        await message.answer("⛔ Нельзя заблокировать администратора.")
        return

    # Бан
    try:
        await bot.ban_chat_member(chat_id, target.id)
        await message.answer(
            f"🚫 <b>{target.first_name}</b> заблокирован.\n"
            f"Заблокировал: {message.from_user.first_name}"
        )
        logger.info(f"Забанен {target.id} в чате {chat_id}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@dp.message(Command("unban"))
async def cmd_unban(message: types.Message):
    if message.chat.type == "private":
        await message.answer("⛔ Эта команда работает только в группе.")
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    sender = await bot.get_chat_member(chat_id, user_id)

    if sender.status not in ["creator", "administrator"]:
        await message.answer("⛔ У вас нет прав для использования этой команды.")
        return

    bot_member = await bot.get_chat_member(chat_id, bot.id)
    if not bot_member.can_restrict_members:
        await message.answer("⛔ Бот не имеет прав для разблокировки пользователей.")
        return

    if not message.text or len(message.text.split()) < 2:
        await message.answer("ℹ️ Использование: /unban @username")
        return

    username = message.text.split()[1].replace("@", "")
    
    try:
        await bot.unban_chat_member(chat_id, username)
        await message.answer(
            f"✅ Пользователь @{username} разблокирован.\n"
            f"Разблокировал: {message.from_user.first_name}"
        )
        logger.info(f"Разбанен @{username} в чате {chat_id}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@dp.message(Command("mute"))
async def cmd_mute(message: types.Message):
    if message.chat.type == "private":
        await message.answer("⛔ Эта команда работает только в группе.")
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    sender = await bot.get_chat_member(chat_id, user_id)

    if sender.status not in ["creator", "administrator"]:
        await message.answer("⛔ У вас нет прав для использования этой команды.")
        return

    bot_member = await bot.get_chat_member(chat_id, bot.id)
    if not bot_member.can_restrict_members:
        await message.answer("⛔ Бот не имеет прав для ограничения пользователей.")
        return

    target = None

    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif message.text and len(message.text.split()) > 1:
        username = message.text.split()[1].replace("@", "")
        try:
            target = await bot.get_chat_member(chat_id, username)
            target = target.user
        except:
            await message.answer("❌ Пользователь не найден.")
            return
    else:
        await message.answer("ℹ️ Использование: /mute @username или ответьте на сообщение.")
        return

    target_member = await bot.get_chat_member(chat_id, target.id)
    if target_member.status in ["creator", "administrator"]:
        await message.answer("⛔ Нельзя ограничить администратора.")
        return

    try:
        await bot.restrict_chat_member(chat_id, target.id, permissions=types.ChatPermissions(can_send_messages=False))
        await message.answer(
            f"🔇 <b>{target.first_name}</b> лишён права голоса.\n"
            f"Ограничил: {message.from_user.first_name}"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@dp.message(Command("unmute"))
async def cmd_unmute(message: types.Message):
    if message.chat.type == "private":
        await message.answer("⛔ Эта команда работает только в группе.")
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    sender = await bot.get_chat_member(chat_id, user_id)

    if sender.status not in ["creator", "administrator"]:
        await message.answer("⛔ У вас нет прав.")
        return

    bot_member = await bot.get_chat_member(chat_id, bot.id)
    if not bot_member.can_restrict_members:
        await message.answer("⛔ Бот не имеет прав.")
        return

    target = None

    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif message.text and len(message.text.split()) > 1:
        username = message.text.split()[1].replace("@", "")
        try:
            target = await bot.get_chat_member(chat_id, username)
            target = target.user
        except:
            await message.answer("❌ Пользователь не найден.")
            return
    else:
        await message.answer("ℹ️ Использование: /unmute @username")
        return

    try:
        await bot.restrict_chat_member(chat_id, target.id, permissions=types.ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        ))
        await message.answer(f"🔊 <b>{target.first_name}</b> снова может говорить.")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

# --- ЗАПУСК (POLLING) ---
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен.")
