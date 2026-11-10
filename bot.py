import os
import telebot
from telebot import types
import datetime

# Render'da Environment Variables (BOT_TOKEN) bo'lsa o'shani oladi, 
# bo'lmasa pastdagi qo'shtirnoq ichiga o'z tokeningizni yozib qo'yishingiz ham mumkin:
TOKEN = os.getenv("BOT_TOKEN", "SIZNING_BOT_TOKENINGIZ")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = (
        "Assalomu alaykum! Vazifalar nazorati botiga xush kelibsiz.\n\n"
        "Vazifa qo'shish formati:\n"
        "<code>/vazifa bolim, Ism, Vazifa tafsiloti, Muddat</code>\n\n"
        "Misol:\n"
        "<code>/vazifa avtokara, ILHOM, leboyotka sotib olish kerak daff ga 917715040, 15-noyabrgachan</code>"
    )
    bot.reply_to(message, text, parse_mode="HTML")

@bot.message_handler(commands=['vazifa'])
def handle_vazifa(message):
    raw_text = message.text.replace('/vazifa', '').strip()
    
    if not raw_text:
        bot.reply_to(
            message, 
            "⚠️ Format noto'g'ri!\nMisol: <code>/vazifa bolim, mas'ul, vazifa, muddat</code>", 
            parse_mode="HTML"
        )
        return

    # Vergul orqali qismlarga ajratamiz
    parts = [p.strip() for p in raw_text.split(',') if p.strip()]

    if len(parts) >= 4:
        bolim = parts[0]
        masul = parts[1]
        muddat = parts[-1]
        vazifa_matni = ", ".join(parts[2:-1])
    elif len(parts) == 3:
        bolim = parts[0]
        masul = parts[1]
        vazifa_matni = parts[2]
        muddat = "Belgilanmagan"
    else:
        bolim = "Umumiy"
        masul = "Belgilanmagan"
        vazifa_matni = raw_text
        muddat = "Belgilanmagan"

    # Tugma yasash
    markup = types.InlineKeyboardMarkup()
    btn_done = types.InlineKeyboardButton("✅ Bajarildi deb belgilash", callback_data="task_done")
    markup.add(btn_done)

    javob = (
        f"📌 <b>Yangi vazifa biriktirildi!</b>\n\n"
        f"🏢 <b>Bo'lim:</b> {bolim}\n"
        f"👤 <b>Mas'ul:</b> {masul}\n"
        f"📝 <b>Vazifa:</b> {vazifa_matni}\n"
        f"⏳ <b>Muddat:</b> {muddat}\n"
        f"📅 <b>Qo'shilgan vaqt:</b> {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        f"Holat: ⏳ <i>Jarayonda...</i>"
    )

    bot.send_message(message.chat.id, javob, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "task_done")
def callback_done(call):
    user_name = call.from_user.first_name
    old_text = call.message.text or ""

    new_text = old_text.replace("Holat: ⏳ Jarayonda...", f"Holat: ✅ <b>Bajarildi!</b> (Tasdiqladi: @{call.from_user.username or user_name})")

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=new_text,
        parse_mode="HTML",
        reply_markup=None
    )
    bot.answer_callback_query(call.id, "Vazifa bajarildi!")

if __name__ == "__main__":
    print("Bot muvaffaqiyatli ishga tushdi...")
    bot.infinity_polling()
