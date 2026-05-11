from flask import Flask, render_template, request, jsonify, redirect, url_for
import threading
import asyncio
import logging
from bot import start_bot, bot
from config import BOT_TOKEN, WEBAPP_URL
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Хранилище платежей (в production используй БД)
payments = {}
users = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-payment', methods=['POST'])
def create_payment():
    data = request.json
    amount = data.get('amount')
    telegram_id = data.get('telegram_id')
    payment_method = data.get('payment_method', 'crypto')
    
    # Генерируем уникальный ID платежа
    payment_id = str(uuid.uuid4())
    
    # Создаем платеж
    payments[payment_id] = {
        'id': payment_id,
        'amount': amount,
        'telegram_id': telegram_id,
        'method': payment_method,
        'status': 'pending',
        'created_at': datetime.now()
    }
    
    # Отправляем уведомление через бота
    if telegram_id:
        asyncio.run_coroutine_threadsafe(
            send_payment_notification(telegram_id, amount, payment_id),
            bot.loop
        )
    
    return jsonify({
        'payment_id': payment_id,
        'status': 'pending',
        'payment_url': f'{WEBAPP_URL}/pay/{payment_id}'
    })

async def send_payment_notification(telegram_id, amount, payment_id):
    """Отправка уведомления о платеже через бота"""
    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=f"🔔 Создан новый платеж:\n\n"
                 f"💰 Сумма: {amount} USDT\n"
                 f"🆔 ID: {payment_id}\n"
                 f"📱 Для оплаты перейдите по ссылке: {WEBAPP_URL}/pay/{payment_id}"
        )
    except Exception as e:
        logging.error(f"Error sending notification: {e}")

@app.route('/pay/<payment_id>')
def pay_page(payment_id):
    payment = payments.get(payment_id)
    if not payment:
        return "Payment not found", 404
    return render_template('payment.html', payment=payment)

@app.route('/check-status/<payment_id>')
def check_status(payment_id):
    payment = payments.get(payment_id)
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    return jsonify({'status': payment['status']})

@app.route('/webhook/crypto', methods=['POST'])
def crypto_webhook():
    """Webhook для подтверждения крипто-платежа"""
    data = request.json
    payment_id = data.get('payment_id')
    
    if payment_id in payments:
        payments[payment_id]['status'] = 'completed'
        payments[payment_id]['tx_hash'] = data.get('tx_hash')
        
        # Отправляем подтверждение через бота
        if payments[payment_id]['telegram_id']:
            asyncio.run_coroutine_threadsafe(
                send_payment_confirmation(payments[payment_id]),
                bot.loop
            )
    
    return jsonify({'status': 'ok'})

async def send_payment_confirmation(payment):
    """Отправка подтверждения оплаты"""
    try:
        await bot.send_message(
            chat_id=payment['telegram_id'],
            text=f"✅ Платеж #{payment['id']} успешно выполнен!\n"
                 f"💰 Сумма: {payment['amount']} USDT\n"
                 f"🔗 TX Hash: {payment.get('tx_hash', 'N/A')}"
        )
    except Exception as e:
        logging.error(f"Error sending confirmation: {e}")

def run_flask():
    app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    # Запускаем бота в главном потоке (long-polling)
    start_bot()
