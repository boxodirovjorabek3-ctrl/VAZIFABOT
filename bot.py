import os
import threading
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot 24/7 faol ishlamoqda!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

TOKEN = "9167869830:AAFqagQexFokD9WNHQoYtDF3bpgxXJKge-M"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['vazifa', 'task'])
def create_task(message):
    raw_text = message.text.replace('/vazifa', '').replace('/task', '').strip()
    
    # Buyruq xabarini guruhdan o'chirish
    try:
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception:
        pass

    if not raw_text:
        return

    department = None
    assignee = None
    task_text = raw_text

    # Format: Bo'lim | Vazifa | Mas'ul
    if "|" in raw_text:
        parts = [p.strip() for p in raw_text.split("|") if p.strip()]
        if len(parts) == 1:
            task_text = parts[0]
        elif len(parts) == 2:
            department = parts[0]
            task_text = parts[1]
        elif len(parts) >= 3:
            department = parts[0]
            task_text = parts[1]
            assignee = parts[2]
    elif ":" in raw_text:
        parts = raw_text.split(":", 1)
        department = parts[0].strip()
        task_text = parts[1].strip()

    caption = "📌 *YANGI TOPSHIRIQ*\n"
    if department:
        caption += f"🏢 *Bo‘lim:* {department}\n"
    if assignee:
        caption += f"👤 *Mas’ul:* {assignee}\n"
    caption += f"\n▫️ {task_text}\n\n⏳ _Holati: Jarayonda_"

    markup = InlineKeyboardMarkup()
    done_button = InlineKeyboardButton(text="🔘 Bajarilmadi (Kutilmoqda)", callback_data="mark_done")
    markup.add(done_button)

    bot.send_message(message.chat.id, caption, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "mark_done")
def callback_done(call):
    user_name = call.from_user.first_name
    original_text = call.message.text

    updated_text = f"{original_text}\n\n✅ *Bajarildi!*\n👤 Qabul qildi: {user_name}"

    markup = InlineKeyboardMarkup()
    finished_btn = InlineKeyboardButton(text=f"✅ Bajarildi ({user_name})", callback_data="already_done")
    markup.add(finished_btn)

    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=updated_text, reply_markup=markup, parse_mode="Markdown")
        bot.answer_callback_query(call.id, text="Qabul qilindi!")
    except Exception:
        bot.answer_callback_query(call.id, text="Bu vazifa allaqachon yopilgan!")

@bot.callback_query_handler(func=lambda call: call.data == "already_done")
def already_done(call):
    bot.answer_callback_query(call.id, text="Bu vazifa allaqachon bajarilgan!")

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    print("Bot ishga tushdi...")
    bot.infinity_polling()
