import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

BOT_TOKEN = os.environ.get("8726943512:AAHwoApr2PQ6AX1pASNoHoawFfBXGWZC5_4")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "8513593166"))
SERVER_IP = os.environ.get("SERVER_IP", "play.heromine.uz")
SERVER_PORT = os.environ.get("SERVER_PORT", "25565")

DONATE_PACKAGES = {
    "vip": {"name": "⭐ VIP", "price": "10,000 so'm", "perks": "- /fly\n- VIP prefix\n- 1.5x XP boost", "duration": "30 kun"},
    "premium": {"name": "💎 PREMIUM", "price": "25,000 so'm", "perks": "- VIP + /kit premium\n- 2x XP boost", "duration": "30 kun"},
    "elite": {"name": "👑 ELITE", "price": "50,000 so'm", "perks": "- Premium + /god\n- 3x XP boost", "duration": "30 kun"},
    "legend": {"name": "🔥 LEGEND", "price": "100,000 so'm", "perks": "- Elite + /speed\n- 5x XP boost", "duration": "30 kun"}
}

PAYMENT_METHODS = {"click": "💳 Click", "payme": "💳 Payme", "uzcard": "💳 UzCard", "crypto": "₿ Crypto"}
PAYMENT_DETAILS = {
    "click": "Click: +998 XX XXX XX XX",
    "payme": "Payme: +998 XX XXX XX XX",
    "uzcard": "UzCard: 8600 XXXX XXXX XXXX",
    "crypto": "USDT TRC20: TXXXXXXXXXXXXXXx"
}

WAITING_NICKNAME, WAITING_PAYMENT_PROOF = range(2)
user_orders = {}
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛒 Donate Sotib Olish", callback_data="donate")],
        [InlineKeyboardButton("📋 Paketlar", callback_data="packages")],
        [InlineKeyboardButton("🖥️ Server", callback_data="server_info")],
        [InlineKeyboardButton("📞 Yordam", callback_data="help")],
    ]
    await update.message.reply_text(
        f"🎮 *HEROMINE DONATE BOT*\n\nServer: `{SERVER_IP}:{SERVER_PORT}`\n\nTugma tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    back_btn = [[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]]

    if data == "packages":
        text = "📦 *DONATE PAKETLARI*\n\n"
        for pkg in DONATE_PACKAGES.values():
            text += f"{pkg['name']} — *{pkg['price']}* ({pkg['duration']})\n{pkg['perks']}\n\n"
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(back_btn), parse_mode='Markdown')

    elif data == "server_info":
        await query.edit_message_text(
            f"🖥️ *SERVER*\n\n🌐 IP: `{SERVER_IP}`\n🔌 Port: `{SERVER_PORT}`\n🎮 Versiya: 1.8-1.20",
            reply_markup=InlineKeyboardMarkup(back_btn), parse_mode='Markdown'
        )

    elif data == "help":
        await query.edit_message_text(
            "📞 *YORDAM*\n\nAdmin: @admin_username\nVaqt: 09:00-22:00",
            reply_markup=InlineKeyboardMarkup(back_btn), parse_mode='Markdown'
        )

    elif data == "donate":
        keyboard = [[InlineKeyboardButton(f"{p['name']} — {p['price']}", callback_data=f"buy_{k}")] for k, p in DONATE_PACKAGES.items()]
        keyboard.append(back_btn[0])
        await query.edit_message_text("🛒 *PAKET TANLANG:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data.startswith("buy_"):
        pkg_key = data[4:]
        pkg = DONATE_PACKAGES[pkg_key]
        context.user_data["selected_package"] = pkg_key
        user_orders[query.from_user.id] = {"package": pkg_key}
        await query.edit_message_text(
            f"✅ *{pkg['name']}* — {pkg['price']}\n\n📝 Minecraft nicknamingizni yuboring:",
            parse_mode='Markdown'
        )
        return WAITING_NICKNAME

    elif data.startswith("pay_"):
        method_key = data[4:]
        pkg_key = context.user_data.get("selected_package")
        pkg = DONATE_PACKAGES[pkg_key]
        if query.from_user.id in user_orders:
            user_orders[query.from_user.id]["payment"] = method_key
        await query.edit_message_text(
            f"💳 *{PAYMENT_METHODS[method_key]}*\n\nPaket: {pkg['name']} — *{pkg['price']}*\n\n`{PAYMENT_DETAILS[method_key]}`\n\nTo'lovdan so'ng *chek screenshot* yuboring!",
            parse_mode='Markdown'
        )
        return WAITING_PAYMENT_PROOF

    elif data == "back_main":
        keyboard = [
            [InlineKeyboardButton("🛒 Donate Sotib Olish", callback_data="donate")],
            [InlineKeyboardButton("📋 Paketlar", callback_data="packages")],
            [InlineKeyboardButton("🖥️ Server", callback_data="server_info")],
            [InlineKeyboardButton("📞 Yordam", callback_data="help")],
        ]
        await query.edit_message_text("🎮 *HEROMINE DONATE BOT*\n\nTugma tanlang:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def receive_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nickname = update.message.text
    context.user_data["nickname"] = nickname
    if update.from_user.id in user_orders:
        user_orders[update.from_user.id]["nickname"] = nickname
    keyboard = [[InlineKeyboardButton(name, callback_data=f"pay_{key}")] for key, name in PAYMENT_METHODS.items()]
    await update.message.reply_text(
        f"✅ Nickname: *{nickname}*\n\n💳 To'lov usuli tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown'
    )
    return WAITING_PAYMENT_PROOF

async def receive_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.from_user
    pkg_key = context.user_data.get("selected_package", "unknown")
    nickname = context.user_data.get("nickname", "unknown")
    pkg = DONATE_PACKAGES.get(pkg_key, {"name": pkg_key, "price": "?"})
    caption = f"🆕 *YANGI DONATE!*\n\n👤 {user.first_name} (@{user.username or 'yoq'})\n🆔 `{user.id}`\n🎮 `{nickname}`\n📦 {pkg['name']} — {pkg['price']}\n\n`/confirm {user.id} {pkg_key} {nickname}`"
    try:
        if update.message.photo:
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=caption, parse_mode='Markdown')
        else:
            await context.bot.send_message(chat_id=ADMIN_ID, text=caption, parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Admin xato: {e}")
    await update.message.reply_text(f"✅ *Qabul qilindi!*\n\nNickname: `{nickname}`\n⏳ 5-10 daqiqada rank beriladi!", parse_mode='Markdown')
    return ConversationHandler.END

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Admin emas!")
        return
    try:
        uid, pkg_key, nick = int(context.args[0]), context.args[1], context.args[2]
        pkg = DONATE_PACKAGES.get(pkg_key, {"name": pkg_key})
        await context.bot.send_message(chat_id=uid, text=f"🎉 *TABRIKLAYMIZ!*\n\nPaket: *{pkg['name']}*\nNickname: `{nick}`\n\n🌐 `{SERVER_IP}`", parse_mode='Markdown')
        await update.message.reply_text(f"✅ {nick} ga {pkg['name']} berildi!")
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi.")
    return ConversationHandler.END

def main():
    print("🤖 Bot ishga tushmoqda...")
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^buy_")],
        states={
            WAITING_NICKNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_nickname)],
            WAITING_PAYMENT_PROOF: [
                MessageHandler(filters.PHOTO | filters.TEXT & ~filters.COMMAND, receive_payment_proof),
                CallbackQueryHandler(button_handler, pattern="^pay_")
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("confirm", confirm_payment))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(button_handler))
    print("✅ Bot tayyor!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()