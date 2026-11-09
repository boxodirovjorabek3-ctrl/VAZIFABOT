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

waiting_for_comment = {}

def get_markup(is_done=False, user_name=""):
    markup = InlineKeyboardMarkup()
    if not is_done:
        done_btn = InlineKeyboardButton(text="🔘 Bajarilmadi (Kutilmoqda)", callback_data="mark_done")
        comment_btn = InlineKeyboardButton(text="💬 Izoh qoldirish", callback_data="add_comment")
        markup.row(done_btn)
        markup.row(comment_btn)
    else:
        done_btn = InlineKeyboardButton(text=f"✅ Bajarildi ({user_name})", callback_data="already_done")
        comment_btn = InlineKeyboardButton(text="💬 Izoh qoldirish", callback_data="add_comment")
        markup.row(done_btn)
        markup.row(comment_btn)
    return markup

@bot.message_handler(commands=['vazifa', 'task'])
def create_task(message):
    raw_text = message.text.replace('/vazifa', '').replace('/task', '').strip()
    
    try:
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception:
        pass

    if not raw_text:
        return

    department = None
    assignee = None
    deadline = None
    task_text = raw_text

    delimiter = "," if "," in raw_text else ("|" if "|" in raw_text else None)

    if delimiter:
        parts = [p.strip() for p in raw_text.split(delimiter) if p.strip()]
        if len(parts) == 1:
            task_text = parts[0]
        elif len(parts) == 2:
            department = parts[0]
            task_text = parts[1]
        elif len(parts) == 3:
            department = parts[0]
            task_text = parts[1]
            assignee = parts[2]
        elif len(parts) >= 4:
            department = parts[0]
            task_text = parts[1]
            assignee = parts[2]
            deadline = parts[3]

    caption = "⚡️ *TEZ KEL | VAZIFA*\n\n"
    if department:
        caption += f"🔴 *BO‘LIM:* ❪ *{department.upper()}* ❫\n\n"
    if assignee:
        caption += f"👤 *Mas’ul:* {assignee}\n"
    if deadline:
        caption += f"⏰ *Muddat:* {deadline}\n"
        
    caption += f"\n▫️ *Topshiriq:* {task_text}\n\n⏳ _Holati: Jarayonda_"

    bot.send_message(message.chat.id, caption, reply_markup=get_markup(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "mark_done")
def callback_done(call):
    user_name = call.from_user.first_name
    original_text = call.message.text

    if "✅ Bajarildi!" in original_text or "Bajaruvchi:" in original_text:
        bot.answer_callback_query(call.id, text="Bu vazifa allaqachon bajarilgan!")
        return

    updated_text = original_text.replace("⏳ Holati: Jarayonda", f"✅ *Holati:* Bajarildi\n👤 *Bajaruvchi:* {user_name}")
    if "Holati: Jarayonda" not in original_text:
        updated_text = f"{original_text}\n\n✅ *Bajarildi!*\n👤 *Bajaruvchi:* {user_name}"

    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=updated_text, reply_markup=get_markup(is_done=True, user_name=user_name), parse_mode="Markdown")
        bot.answer_callback_query(call.id, text="Vazifa bajarildi deb belgilandi!")
    except Exception:
        bot.answer_callback_query(call.id, text="Yangilab bo'lmadi.")

@bot.callback_query_handler(func=lambda call: call.data == "already_done")
def already_done(call):
    bot.answer_callback_query(call.id, text="Bu vazifa allaqachon bajarilgan!")

@bot.callback_query_handler(func=lambda call: call.data == "add_comment")
def request_comment(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    target_msg_id = call.message.message_id
    user_name = call.from_user.first_name

    waiting_for_comment[f"{chat_id}_{user_id}"] = target_msg_id

    bot.answer_callback_query(call.id)
    sent_prompt = bot.send_message(
        chat_id, 
        f"✍️ *{user_name}*, ushbu vazifaga izohingizni yozing:", 
        parse_mode="Markdown"
    )
    waiting_for_comment[f"{chat_id}_{user_id}_prompt"] = sent_prompt.message_id

@bot.message_handler(func=lambda m: f"{m.chat.id}_{m.from_user.id}" in waiting_for_comment)
def handle_comment_reply(message):
    key = f"{message.chat.id}_{message.from_user.id}"
    target_msg_id = waiting_for_comment.pop(key, None)
    prompt_id = waiting_for_comment.pop(f"{key}_prompt", None)

    try:
        bot.delete_message(message.chat.id, message.message_id)
        if prompt_id:
            bot.delete_message(message.chat.id, prompt_id)
    except Exception:
        pass

    if not target_msg_id:
        return

    try:
        user_name = message.from_user.first_name
        comment_text = message.text

        bot.send_message(
            message.chat.id, 
            f"💬 *{user_name}* topshiriqqa izoh qoldirdi:\n«_{comment_text}_»", 
            reply_to_message_id=target_msg_id,
            parse_mode="Markdown"
        )
    except Exception:
        pass

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    print("Bot ishga tushdi...")
    bot.infinity_polling()
