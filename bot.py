import os
import threading
from flask import Flask
import telebot
from telebot import types

TOKEN = "9167869830:AAGlK7JpP74rSDAY3Gj8E0Nm4Yu4oqeoWIM"

bot = telebot.TeleBot(TOKEN)

# Render uchun web-server
server = Flask(__name__)

@server.route("/")
def home():
    return "Bot ishlab turibdi!", 200

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server.run(host="0.0.0.0", port=port)

# /start va /help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = (
        "⚡️ <b>TEZ KEL | VAZIFA BOTI</b>\n\n"
        "Vazifa kiritish namunasi:\n"
        "<code>/vazifa bolim, Mas'ul, Muddat, Topshiriq matni</code>\n\n"
        "Misol:\n"
        "<code>/vazifa EVAKUATOR, mamur, 12-noyabr, hamma remont bolgan moshinalarni royhati narhi javdalini qilib chiqsh</code>"
    )
    bot.reply_to(message, text, parse_mode="HTML")

# /vazifa buyrug'i
@bot.message_handler(commands=['vazifa'])
def handle_vazifa(message):
    # Foydalanuvchi yozgan /vazifa xabarini darhol o'chirib yuborish
    try:
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception:
        pass

    raw_text = message.text.replace('/vazifa', '').strip()
    # Guruhda bot nomini qo'shib yozilgan holat uchun tozalash (/vazifa@bot_nomi)
    if raw_text.startswith('@'):
        raw_text = raw_text.split(' ', 1)[1] if ' ' in raw_text else ''
    
    if not raw_text:
        warning = bot.send_message(
            message.chat.id, 
            "⚠️ <b>Format xato!</b>\nNamuna: <code>/vazifa Bo'lim, Mas'ul, Muddat, Topshiriq</code>", 
            parse_mode="HTML"
        )
        return

    parts = [p.strip() for p in raw_text.split(',') if p.strip()]

    if len(parts) >= 4:
        bolim = parts[0].upper()
        masul = parts[1]
        muddat = parts[2]
        topshiriq = ", ".join(parts[3:])
    elif len(parts) == 3:
        bolim = parts[0].upper()
        masul = parts[1]
        muddat = parts[2]
        topshiriq = "Kiritilmagan"
    else:
        bolim = "UMUMIY"
        masul = "Belgilanmagan"
        muddat = "Belgilanmagan"
        topshiriq = raw_text

    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_status = types.InlineKeyboardButton("🔘 Bajarilmadi (Kutilmoqda)", callback_data="toggle_status")
    btn_comment = types.InlineKeyboardButton("💬 Izoh qoldirish", callback_data="add_comment")
    markup.add(btn_status, btn_comment)

    javob = (
        f"⚡️ <b>TEZ KEL | VAZIFA</b>\n\n"
        f"🔴 <b>BO'LIM: ( {bolim} )</b>\n\n"
        f"👤 <b>Mas'ul:</b> {masul}\n"
        f"⏰ <b>Muddat:</b> {muddat}\n\n"
        f"▫️ <b>Topshiriq:</b> {topshiriq}\n\n"
        f"⏳ <i>Holati: Jarayonda</i>"
    )

    sent_msg = bot.send_message(message.chat.id, javob, reply_markup=markup, parse_mode="HTML")

    # Chiqqan vazifani avtomatik zakrepit qilish
    try:
        bot.pin_chat_message(chat_id=message.chat.id, message_id=sent_msg.message_id, disable_notification=True)
    except Exception:
        pass

# Tugmalar bosilganda
@bot.callback_query_handler(func=lambda call: call.data in ["toggle_status", "add_comment"])
def callback_handler(call):
    if call.data == "toggle_status":
        user_mention = f"@{call.from_user.username}" if call.from_user.username else call.from_user.first_name
        current_text = call.message.text or ""

        if "⏳ Holati: Jarayonda" in current_text:
            new_text = current_text.replace(
                "⏳ Holati: Jarayonda", 
                f"✅ <b>Holati: Bajarildi!</b> (Tasdiqladi: {user_mention})"
            )
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn_status = types.InlineKeyboardButton("✅ Bajarildi", callback_data="toggle_status")
            btn_comment = types.InlineKeyboardButton("💬 Izoh qoldirish", callback_data="add_comment")
            markup.add(btn_status, btn_comment)
            
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=new_text,
                parse_mode="HTML",
                reply_markup=markup
            )

            # Bajarilganda zakrepitdan chiqarib tashlash
            try:
                bot.unpin_chat_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            except Exception:
                pass

            bot.answer_callback_query(call.id, "Vazifa bajarildi va zakrepitdan yechildi!")
        else:
            bot.answer_callback_query(call.id, "Ushbu vazifa allaqachon bajarilgan!")

    elif call.data == "add_comment":
        bot.answer_callback_query(
            call.id, 
            "Izoh qoldirish uchun xabarga 'Reply' (Javob berish) qilib yozing.", 
            show_alert=True
        )

if __name__ == "__main__":
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()
    
    print("Bot muvaffaqiyatli ishga tushdi...")
    bot.infinity_polling()
