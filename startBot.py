YOUR_CHAT_ID =5709854483

import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from llama_cpp import Llama
import threading
 
 
   
   #       تحميل النموذج
llm = Llama(model_path="llama-2-7b.Q4_K_M.gguf")

# الاتصال بقاعدة البيانات
def get_db_connection():
    conn = sqlite3.connect('bot.db')
    conn.row_factory = sqlite3.Row
    return conn

# تخزين بيانات الحساب
def save_account(user_id, platform, email, password):
    conn = get_db_connection()
    conn.execute('INSERT INTO accounts (user_id, platform, email, password) VALUES (?, ?, ?, ?)', 
                 (user_id, platform, email, password))
    conn.commit()
    conn.close()

# عرض الحسابات
def view_accounts(user_id):
    conn = get_db_connection()
    accounts = conn.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    return accounts

# بدء البوت
def start(update: Update, context: CallbackContext):
    if update.message.chat_id != YOUR_CHAT_ID:
        update.message.reply_text("غير مصرح لك باستخدام هذا البوت.")
        return

    keyboard = [
        [InlineKeyboardButton("إدارة الحسابات", callback_data='manage_accounts')],
        [InlineKeyboardButton("أتمتة المهام", callback_data='automate_tasks')],
        [InlineKeyboardButton("عرض التقارير", callback_data='view_reports')],
        [InlineKeyboardButton("التحدث مع الذكاء الاصطناعي", callback_data='chat_with_ai')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('اختر خيارًا:', reply_markup=reply_markup)

# إضافة حساب
def add_account(update: Update, context: CallbackContext):
    if update.message.chat_id != YOUR_CHAT_ID:
        update.message.reply_text("غير مصرح لك باستخدام هذا البوت.")
        return

    platform = context.args[0]
    email = context.args[1]
    password = context.args[2]
    save_account(YOUR_CHAT_ID, platform, email, password)
    update.message.reply_text(f"تمت إضافة الحساب على {platform}.")

# عرض الحسابات
def view_accounts_command(update: Update, context: CallbackContext):
    if update.message.chat_id != YOUR_CHAT_ID:
        update.message.reply_text("غير مصرح لك باستخدام هذا البوت.")
        return

    accounts = view_accounts(YOUR_CHAT_ID)
    if accounts:
        message = "\n".join([f"{account['platform']}: {account['email']}" for account in accounts])
        update.message.reply_text(f"الحسابات:\n{message}")
    else:
        update.message.reply_text("لا توجد حسابات مضافة.")

# التحدث مع الذكاء الاصطناعي
def chat_with_ai(update: Update, context: CallbackContext):
    if update.message.chat_id != YOUR_CHAT_ID:
        update.message.reply_text("غير مصرح لك باستخدام هذا البوت.")
        return

    # الحصول على النص من المستخدم
    user_input = update.message.text

    # إرسال النص إلى النموذج
    response = llm(user_input, max_tokens=100)

    # إرسال الرد إلى المستخدم
    update.message.reply_text(response['choices'][0]['text'])

# تشغيل البوت
def main():
    # إنشاء جداول قاعدة البيانات إذا لم تكن موجودة
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, platform TEXT NOT NULL, email TEXT NOT NULL, password TEXT NOT NULL)')
    conn.close()

    # استبدل 'YOUR_TELEGRAM_BOT_TOKEN' بالتوكن الخاص بك
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN", use_context=True)
    dispatcher = updater.dispatcher

    # إضافة الأوامر
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add_account", add_account))
    dispatcher.add_handler(CommandHandler("view_accounts", view_accounts_command))
    dispatcher.add_handler(CommandHandler("chat_with_ai", chat_with_ai))

    # بدء البوت
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()