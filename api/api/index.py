import os
import json
import telebot
from flask import Flask, request

TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])

bot = telebot.TeleBot(TOKEN)
app = Flask(name)

@app.route("/", methods=["GET"])
def home():
return "Relax Massage Bot is running", 200

@app.route("/api/webhook", methods=["POST"])
def webhook():
update = request.get_data().decode("utf-8")
bot.process_new_updates([telebot.types.Update.de_json(update)])
return "OK", 200

@bot.message_handler(commands=["start"])
def start(message):
bot.send_message(
message.chat.id,
"أهلاً بيك في ريلاكس مساج 🌹\n\n"
"رسوم التواصل: 50 جنيه.\n"
"حوّل المبلغ على فودافون كاش:\n"
"01120069155\n\n"
"بعد التحويل، ابعت صورة الإيصال هنا "
"وسيتم مراجعته يدويًا."
)

@bot.message_handler(content_types=["photo"])
def receipt(message):
bot.send_message(
ADMIN_ID,
f"إيصال دفع جديد من المستخدم: {message.from_user.id}",
reply_markup=approval_buttons(message.from_user.id)
)
bot.send_photo(
ADMIN_ID,
message.photo[-1].file_id,
caption="راجع الإيصال قبل الموافقة."
)
bot.reply_to(message, "تم استلام الإيصال، انتظر مراجعة الدفع.")

def approval_buttons(user_id):
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
keyboard = InlineKeyboardMarkup()
keyboard.add(
InlineKeyboardButton("موافقة ✅", callback_data=f"approve:{user_id}"),
InlineKeyboardButton("رفض ❌", callback_data=f"reject:{user_id}")
)
return keyboard

@bot.callback_query_handler(func=lambda call: call.data.startswith(("approve:", "reject:")))
def review(call):
if call.from_user.id != ADMIN_ID:
bot.answer_callback_query(call.id, "غير مسموح.")
return

action, user_id = call.data.split(":")
user_id = int(user_id)

if action == "approve":
    contact_link = os.environ.get("CONTACT_LINK")
    if contact_link:
        bot.send_message(user_id, f"تم تأكيد الدفع ✅\nرابط التواصل: {contact_link}")
    else:
        bot.send_message(user_id, "تم تأكيد الدفع ✅\nتواصل مع الإدارة للحصول على رابط التواصل.")
    bot.answer_callback_query(call.id, "تمت الموافقة.")
else:
    bot.send_message(user_id, "تعذر تأكيد الإيصال. تواصل مع الإدارة.")
    bot.answer_callback_query(call.id, "تم الرفض.")
