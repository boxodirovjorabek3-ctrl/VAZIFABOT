import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "9167869830:AAFqagQexFokD9WNHQoYtDF3bpgxXJKge-M"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['vazifa', 'task'])
def create_task(message):
    task_text = message.text.replace('/vazifa', '').replace('/task', '').strip()
    
    if not task_text:
        bot.reply_to(message, "⚠️ Vazifa matnini yozing!\nMasalan: `/vazifa Buxgalteriya cheklarini yopish`", parse_mode="Markdown")
        return

    markup = InlineKeyboardMarkup()
    done_button = InlineKeyboardButton(text="🔘 Bajarilmadi (Kutilmoqda)", callback_data="mark_done")
    markup.add(done_button)

    caption = f"📌 *YANGI TOPSHIRIQ:*\n\n▫️ {task_text}\n\n⏳ _Holati: Jarayonda_"
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

print("Bot ishga tushdi...")
bot.infinity_polling()
