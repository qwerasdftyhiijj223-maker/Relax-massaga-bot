import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = os.environ["ADMIN_ID"]
PAYMENT_NUMBER = "01120069155"
FEE = "50 جنيه"

bot = telebot.TeleBot(TOKEN)
pending = {}

@bot.message_handler(commands=["start"])
def start(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("طلب التواصل", callback_data="request"))
    bot.send_message(
        message.chat.id,
        "أهلاً بيك في ريلاكس مساج 🌹\n\n"
        f"رسوم التواصل: {FEE}\n"
        f"فودافون كاش: {PAYMENT_NUMBER}\n\n"
        "حوّل الرسوم ثم اضغط طلب التواصل وأرسل صورة الإيصال.",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "request")
def request(call):
    bot.answer_callback_query(call.id)
    pending[call.from_user.id] = call.message.chat.id
    bot.send_message(
        call.message.chat.id,
        "بعد التحويل، ابعت صورة إيصال الدفع هنا للمراجعة."
    )

@bot.message_handler(content_types=["photo"])
def receipt(message):
    uid = str(message.from_user.id)
    if uid not in pending:
        bot.reply_to(message, "اضغط طلب التواصل أولاً من /start.")
        return
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("تأكيد الدفع", callback_data=f"approve:{uid}"),
        InlineKeyboardButton("رفض الإيصال", callback_data=f"reject:{uid}")
    )
    bot.send_photo(
        int(ADMIN_ID),
        message.photo[-1].file_id,
        caption=f"إيصال جديد\nالمستخدم: {uid}\nالاسم: {message.from_user.first_name}",
        reply_markup=keyboard
    )
    bot.reply_to(message, "تم استلام الإيصال، انتظر مراجعة الدفع.")

@bot.callback_query_handler(func=lambda call: call.data.startswith(("approve:", "reject:")))
def review(call):
    if str(call.from_user.id) != ADMIN_ID:
        bot.answer_callback_query(call.id, "غير مسموح.")
        return
    action, uid = call.data.split(":")
    chat_id = pending.get(int(uid))
    if not chat_id:
        bot.answer_callback_query(call.id, "الطلب غير موجود.")
        return
    if action == "approve":
        bot.send_message(chat_id, "تمت الموافقة على الدفع. تواصل مع صاحب الخدمة عبر حسابه الذي سيُرسل لك بشكل منفصل.")
        bot.answer_callback_query(call.id, "تمت الموافقة.")
    else:
        bot.send_message(chat_id, "تعذر قبول الإيصال. راجع التحويل وأرسل إيصالاً واضحاً.")
        bot.answer_callback_query(call.id, "تم رفض الإيصال.")

bot.infinity_polling()
