import os
from flask import Flask, request, abort
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
PAYMENT_NUMBER = "01120069155"
FEE = "50 جنيه"
CONTACT_LINK = os.environ.get("CONTACT_LINK", "")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=["start"])
def start(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        "طلب التواصل", callback_data="request"
    ))
    bot.send_message(
        message.chat.id,
        "أهلاً بيك في ريلاكس مساج 🌹\n\n"
        f"رسوم التواصل: {FEE}\n"
        f"فودافون كاش: {PAYMENT_NUMBER}\n\n"
        "حوّل الرسوم ثم اضغط طلب التواصل "
        "وابعت صورة الإيصال.",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda c: c.data == "request")
def request_contact(call):
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "بعد التحويل، ابعت صورة إيصال الدفع هنا."
    )

@bot.message_handler(content_types=["photo"])
def receipt(message):
    keyboard = InlineKeyboardMarkup()
    uid = message.from_user.id
    keyboard.row(
        InlineKeyboardButton(
            "تأكيد الدفع", callback_data=f"approve:{uid}"
        ),
        InlineKeyboardButton(
            "رفض الإيصال", callback_data=f"reject:{uid}"
        )
    )
    bot.send_photo(
        ADMIN_ID,
        message.photo[-1].file_id,
        caption=(
            f"إيصال للمراجعة\n"
            f"المستخدم: {uid}\n"
            f"الاسم: {message.from_user.first_name}"
        ),
        reply_markup=keyboard
    )
    bot.reply_to(
        message, "استلمنا الإيصال. انتظر مراجعة الدفع."
    )

@bot.callback_query_handler(
    func=lambda c: c.data.startswith(("approve:", "reject:"))
)
def review(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "غير مسموح.")
        return

    action, uid = call.data.split(":")
    uid = int(uid)

    if action == "approve":
        if not CONTACT_LINK:
            bot.answer_callback_query(
                call.id, "رابط التواصل لم يُضف بعد."
            )
            bot.send_message(
                ADMIN_ID,
                "أضف CONTACT_LINK في إعدادات الاستضافة أولاً."
            )
            return

        bot.send_message(
            uid,
            f"تمت الموافقة على الدفع ✅\nرابط التواصل: {CONTACT_LINK}"
        )
        bot.answer_callback_query(call.id, "تمت الموافقة.")
    else:
        bot.send_message(
            uid, "تعذر قبول الإيصال. راجع التحويل وأرسل إيصالاً واضحاً."
        )
        bot.answer_callback_query(call.id, "تم الرفض.")

@app.route("/")
def home():
    return "Relax Massage bot is running", 200

@app.route("/webhook/<secret>", methods=["POST"])
def webhook(secret):
    if secret != TOKEN:
        abort(403)
    update = telebot.types.Update.de_json(
        request.get_data().decode("utf-8")
    )
    bot.process_new_updates([update])
    return "OK", 200

if os.environ.get("RENDER_EXTERNAL_URL"):
    bot.set_webhook(
        url=f"{os.environ['RENDER_EXTERNAL_URL']}/webhook/{TOKEN}"
    )
