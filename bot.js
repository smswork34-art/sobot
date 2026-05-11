const TelegramBot = require('node-telegram-bot-api');
const Database = require('better-sqlite3');
const axios = require('axios');
require('dotenv').config();

// Init
const bot = new TelegramBot(process.env.BOT_TOKEN, { polling: true });
const db = new Database('blackjack.db');
const CRYPTO_API = 'https://pay.crypt.bot/api';

// Database setup
db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id TEXT UNIQUE NOT NULL,
    username TEXT,
    first_name TEXT,
    balance REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS deposits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    invoice_id TEXT UNIQUE,
    amount REAL,
    currency TEXT DEFAULT 'USDT',
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
  );

  CREATE TABLE IF NOT EXISTS withdrawals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL,
    address TEXT,
    currency TEXT DEFAULT 'USDT',
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
  );

  CREATE TABLE IF NOT EXISTS game_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    bet REAL,
    win REAL,
    game_type TEXT DEFAULT 'blackjack',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
  );
`);

// Helper: Get or create user
function getUser(telegramId, username, firstName) {
  let user = db.prepare('SELECT * FROM users WHERE telegram_id = ?').get(telegramId.toString());
  if (!user) {
    db.prepare('INSERT INTO users (telegram_id, username, first_name, balance) VALUES (?, ?, ?, 0)')
      .run(telegramId.toString(), username, firstName);
    user = db.prepare('SELECT * FROM users WHERE telegram_id = ?').get(telegramId.toString());
  }
  return user;
}

// Helper: Create Crypto Bot invoice
async function createInvoice(amount, currency = 'USDT') {
  try {
    const response = await axios.get(`${CRYPTO_API}/createInvoice`, {
      params: {
        asset: currency,
        amount: amount.toString(),
        description: 'Пополнение баланса Blackjack',
        hidden_message: 'Спасибо за пополнение!',
        paid_btn_name: 'openBot',
        paid_btn_url: `https://t.me/${bot.options.username || 'your_bot'}`,
        expires_in: 3600
      },
      headers: {
        'Crypto-Pay-API-Token': process.env.CRYPTO_BOT_TOKEN
      }
    });
    return response.data.result;
  } catch (error) {
    console.error('Create invoice error:', error.response?.data || error.message);
    return null;
  }
}

// Helper: Check invoice status
async function checkInvoice(invoiceId) {
  try {
    const response = await axios.get(`${CRYPTO_API}/getInvoices`, {
      params: { invoice_ids: invoiceId },
      headers: {
        'Crypto-Pay-API-Token': process.env.CRYPTO_BOT_TOKEN
      }
    });
    return response.data.result.items[0];
  } catch (error) {
    console.error('Check invoice error:', error.response?.data || error.message);
    return null;
  }
}

// Helper: Create withdrawal
async function createWithdrawal(userId, amount, address, currency = 'USDT') {
  try {
    const response = await axios.post(`${CRYPTO_API}/transfer`, {
      user_id: userId,
      asset: currency,
      amount: amount.toString(),
      spend_id: `withdraw_${Date.now()}`
    }, {
      headers: {
        'Crypto-Pay-API-Token': process.env.CRYPTO_BOT_TOKEN
      }
    });
    return response.data.result;
  } catch (error) {
    console.error('Withdrawal error:', error.response?.data || error.message);
    return null;
  }
}

// ============ BOT COMMANDS ============

// Start command
bot.onText(/\/start/, async (msg) => {
  const user = getUser(msg.from.id, msg.from.username, msg.from.first_name);
  
  const keyboard = {
    reply_markup: {
      inline_keyboard: [
        [{ text: '🎮 ИГРАТЬ', web_app: { url: 'https://your-domain.com/game.html' } }],
        [
          { text: '💰 Пополнить', callback_data: 'deposit' },
          { text: '💳 Вывести', callback_data: 'withdraw' }
        ],
        [
          { text: '👤 Профиль', callback_data: 'profile' },
          { text: '📊 Статистика', callback_data: 'stats' }
        ]
      ]
    }
  };

  await bot.sendMessage(msg.chat.id, 
    `🎰 *BLACKJACK CASINO*\n\n` +
    `Привет, ${msg.from.first_name}!\n` +
    `Твой баланс: *${user.balance.toFixed(2)} USDT*\n\n` +
    `Выбери действие:`,
    { parse_mode: 'Markdown', ...keyboard }
  );
});

// Profile callback
bot.on('callback_query', async (query) => {
  const user = getUser(query.from.id, query.from.username, query.from.first_name);
  const chatId = query.message.chat.id;

  switch (query.data) {
    case 'profile':
      const stats = db.prepare(`
        SELECT 
          COUNT(*) as total_games,
          SUM(CASE WHEN win > 0 THEN 1 ELSE 0 END) as wins,
          SUM(bet) as total_bet,
          SUM(win) as total_win
        FROM game_history 
        WHERE user_id = ?
      `).get(user.id);

      await bot.sendMessage(chatId,
        `👤 *ПРОФИЛЬ*\n\n` +
        `ID: ${user.telegram_id}\n` +
        `Имя: ${user.first_name}\n` +
        `Баланс: *${user.balance.toFixed(2)} USDT*\n\n` +
        `📊 *Статистика игр:*\n` +
        `Игр сыграно: ${stats.total_games || 0}\n` +
        `Побед: ${stats.wins || 0}\n` +
        `Всего ставок: ${stats.total_bet?.toFixed(2) || 0} USDT\n` +
        `Всего выигрышей: ${stats.total_win?.toFixed(2) || 0} USDT`,
        { parse_mode: 'Markdown' }
      );
      break;

    case 'deposit':
      await showDepositMenu(chatId, user);
      break;

    case 'withdraw':
      await showWithdrawMenu(chatId, user);
      break;

    case 'stats':
      await showStats(chatId, user);
      break;
  }

  await bot.answerCallbackQuery(query.id);
});

// Deposit menu
async function showDepositMenu(chatId, user) {
  const keyboard = {
    reply_markup: {
      inline_keyboard: [
        [
          { text: '10 USDT', callback_data: 'dep_10' },
          { text: '25 USDT', callback_data: 'dep_25' },
          { text: '50 USDT', callback_data: 'dep_50' }
        ],
        [
          { text: '100 USDT', callback_data: 'dep_100' },
          { text: '250 USDT', callback_data: 'dep_250' },
          { text: '500 USDT', callback_data: 'dep_500' }
        ],
        [{ text: '💎 Другая сумма', callback_data: 'dep_custom' }],
        [{ text: '🔙 Назад', callback_data: 'back' }]
      ]
    }
  };

  await bot.sendMessage(chatId,
    `💰 *ПОПОЛНЕНИЕ БАЛАНСА*\n\n` +
    `Текущий баланс: *${user.balance.toFixed(2)} USDT*\n\n` +
    `Выбери сумму пополнения:`,
    { parse_mode: 'Markdown', ...keyboard }
  );
}

// Handle deposit amounts
bot.on('callback_query', async (query) => {
  if (!query.data.startsWith('dep_')) return;
  
  const user = getUser(query.from.id, query.from.username, query.from.first_name);
  const chatId = query.message.chat.id;
  let amount;

  if (query.data === 'dep_custom') {
    await bot.sendMessage(chatId, 'Введи сумму в USDT (минимум 1):');
    // Сохраняем состояние ожидания ввода
    db.prepare('UPDATE users SET temp_state = ? WHERE id = ?').run('awaiting_deposit_amount', user.id);
    await bot.answerCallbackQuery(query.id);
    return;
  }

  amount = parseFloat(query.data.replace('dep_', ''));
  await createDeposit(chatId, user, amount);
  await bot.answerCallbackQuery(query.id);
});

// Handle custom deposit amount
bot.on('message', async (msg) => {
  if (!msg.text || msg.text.startsWith('/')) return;
  
  const user = db.prepare('SELECT * FROM users WHERE telegram_id = ?').get(msg.from.id.toString());
  if (!user || user.temp_state !== 'awaiting_deposit_amount') return;

  const amount = parseFloat(msg.text);
  if (isNaN(amount) || amount < 1) {
    await bot.sendMessage(msg.chat.id, '❌ Введи корректную сумму (минимум 1 USDT)');
    return;
  }

  if (amount > 10000) {
    await bot.sendMessage(msg.chat.id, '❌ Максимальная сумма пополнения: 10,000 USDT');
    return;
  }

  await createDeposit(msg.chat.id, user, amount);
  db.prepare('UPDATE users SET temp_state = NULL WHERE id = ?').run(user.id);
});

// Create deposit invoice
async function createDeposit(chatId, user, amount) {
  const loadingMsg = await bot.sendMessage(chatId, '⏳ Создаю счёт...');

  const invoice = await createInvoice(amount);
  
  if (!invoice) {
    await bot.editMessageText('❌ Ошибка создания счёта. Попробуй позже.', {
      chat_id: chatId,
      message_id: loadingMsg.message_id
    });
    return;
  }

  // Save to database
  db.prepare('INSERT INTO deposits (user_id, invoice_id, amount, currency) VALUES (?, ?, ?, ?)')
    .run(user.id, invoice.invoice_id, amount, 'USDT');

  const keyboard = {
    reply_markup: {
      inline_keyboard: [
        [{ text: '💳 Оплатить', url: invoice.pay_url }],
        [{ text: '🔄 Проверить оплату', callback_data: `check_${invoice.invoice_id}` }]
      ]
    }
  };

  await bot.editMessageText(
    `💰 *Счёт создан!*\n\n` +
    `Сумма: *${amount} USDT*\n` +
    `Счёт действителен 1 час\n\n` +
    `Нажми "Оплатить" для пополнения через Crypto Bot`,
    {
      chat_id: chatId,
      message_id: loadingMsg.message_id,
      parse_mode: 'Markdown',
      ...keyboard
    }
  );
}

// Check payment
bot.on('callback_query', async (query) => {
  if (!query.data.startsWith('check_')) return;
  
  const invoiceId = query.data.replace('check_', '');
  const chatId = query.message.chat.id;
  
  await bot.answerCallbackQuery(query.id, { text: 'Проверяю...' });

  const invoice = await checkInvoice(invoiceId);
  if (!invoice) {
    await bot.sendMessage(chatId, '❌ Ошибка проверки платежа');
    return;
  }

  if (invoice.status === 'paid') {
    // Update user balance
    const deposit = db.prepare('SELECT * FROM deposits WHERE invoice_id = ? AND status = ?')
      .get(invoiceId, 'pending');
    
    if (deposit) {
      db.prepare('UPDATE deposits SET status = ? WHERE invoice_id = ?').run('completed', invoiceId);
      db.prepare('UPDATE users SET balance = balance + ? WHERE id = ?')
        .run(deposit.amount, deposit.user_id);
      
      const user = db.prepare('SELECT * FROM users WHERE id = ?').get(deposit.user_id);
      
      await bot.sendMessage(chatId,
        `✅ *Платёж получен!*\n\n` +
        `Сумма: +${deposit.amount} USDT\n` +
        `Новый баланс: *${user.balance.toFixed(2)} USDT*`,
        { parse_mode: 'Markdown' }
      );
    }
  } else if (invoice.status === 'active') {
    await bot.sendMessage(chatId, '⏳ Платёж ещё не получен. Попробуй позже или оплати снова.');
  } else {
    await bot.sendMessage(chatId, `❌ Статус платежа: ${invoice.status}`);
  }
});

// Withdraw menu
async function showWithdrawMenu(chatId, user) {
  if (user.balance < 1) {
    await bot.sendMessage(chatId, '❌ Минимальная сумма вывода: 1 USDT\nТвой баланс: ' + user.balance.toFixed(2) + ' USDT');
    return;
  }

  const keyboard = {
    reply_markup: {
      inline_keyboard: [
        [{ text: '💳 Вывести на кошелёк', callback_data: 'wd_wallet' }],
        [{ text: '🔙 Назад', callback_data: 'back' }]
      ]
    }
  };

  await bot.sendMessage(chatId,
    `💳 *ВЫВОД СРЕДСТВ*\n\n` +
    `Баланс: *${user.balance.toFixed(2)} USDT*\n` +
    `Мин. вывод: 1 USDT\n` +
    `Комиссия: 0.5%\n\n` +
    `Выбери способ вывода:`,
    { parse_mode: 'Markdown', ...keyboard }
  );
}

// API endpoints for HTML game
const express = require('express');
const app = express();
app.use(express.json());

// CORS for game
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  next();
});

// Get user balance
app.get('/api/user/:telegramId', (req, res) => {
  const user = db.prepare('SELECT * FROM users WHERE telegram_id = ?').get(req.params.telegramId);
  if (!user) return res.json({ error: 'User not found' });
  res.json({ balance: user.balance, firstName: user.first_name });
});

// Update balance after game
app.post('/api/game/result', (req, res) => {
  const { telegramId, bet, win, gameType } = req.body;
  const user = db.prepare('SELECT * FROM users WHERE telegram_id = ?').get(telegramId.toString());
  
  if (!user) return res.json({ error: 'User not found' });
  
  const newBalance = user.balance - bet + win;
  if (newBalance < 0) return res.json({ error: 'Insufficient balance' });

  db.prepare('UPDATE users SET balance = ? WHERE id = ?').run(newBalance, user.id);
  db.prepare('INSERT INTO game_history (user_id, bet, win, game_type) VALUES (?, ?, ?, ?)')
    .run(user.id, bet, win, gameType);

  res.json({ success: true, newBalance });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`API server running on port ${PORT}`));

console.log('🤖 Bot started with polling...');
