#!/usr/bin/env python3
# ============================================
#   HEROMINE MINECRAFT DONATE BOT
#   Telegram Bot - @BotFather dan token oling
# ============================================

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# ============================================
# ⚙️ SOZLAMALAR - O'ZGARTIRING!
# ============================================
BOT_TOKEN = "8726943512:AAEwChsz8E8lG9Zb8buVCetyLK485y2aKMo"  # @BotFather dan olgan tokeningiz
ADMIN_ID = 8513593166  # Sizning Telegram ID (https://t.me/userinfobot dan oling)
SERVER_IP = "play.heromine.uz"  # Server IP
SERVER_PORT = "25565"  # Server Port

# Donate paketlari
DONATE_PACKAGES = {
    "vip": {
        "name": "⭐ VIP",
        "price": "10,000 so'm",
        "perks": "- /fly komandasi\n- Rang berish\n- VIP prefix\n- 1.5x XP boost",
        "duration": "30 kun"
    },
    "premium": {
        "name": "💎 PREMIUM",
        "price": "25,000 so'm",
        "perks": "- VIP barcha imkoniyatlari\n- /kit premium\n- 2x XP boost\n- Ekstra uy",
        "duration": "30 kun"
    },
    "elite": {
        "name": "👑 ELITE",
        "price": "50,000 so'm",
        "perks": "- Premium barcha imkoniyatlari\n- /god mode\n- 3x XP boost\n- Custom prefix",
        "duration": "30 kun"
    },
    "legend": {
        "name": "🔥 LEGEND",
        "price": "100,000 so'm",
        "perks": "- Elite barcha imkoniyatlari\n- /speed /jump\n- 5x XP boost\n- LEGEND prefix\n- Admin bilan muloqot",
        "duration": "30 kun"
    }
}

# To'lov usullari
PAYMENT_METHODS = {
    "click": "💳 Click",
    "payme": "💳 Payme",
    "uzcard": "💳 UzCard",
    "crypto": "₿ Crypto (USDT TRC20)"
}

PAYMENT_DETAILS = {
    "click": "Click: +998 XX XXX XX XX (ISM FAMILYA)",
    "payme": "Payme: +998 XX XXX XX XX (ISM FAMILYA)",
    "uzcard": "UzCard: 8600 XXXX XXXX XXXX (ISM FAMILYA)",
    "crypto": "USDT TRC20: TXXXXXXXXXXXXXXXXXXXXXXx"
}

# ============================================
# Bot holatlari
# ============================================
WAITING_NICKNAME, WAITING_PAYMENT_PROOF = range(2)

# Foydalanuvchi ma'lumotlari (vaqtinchalik)
user_orders = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ============================================
# /start komandasi
# ============================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛒 Donate Sotib Olish", callback_data="donate")],
        [InlineKeyboardButton("📋 Paketlar Ro'yxati", callback_data="packages")],
        [InlineKeyboardButton("🖥️ Server Ma'lumoti", callback_data="server_info")],
        [InlineKeyboardButton("📞 Yordam", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🎮 *HEROMINE DONATE BOT*ga xush kelibsiz!\n\n"
        f"Server: `{SERVER_IP}:{SERVER_PORT}`\n\n"
        f"Bu bot orqali siz serverimizda donate paketlarini sotib olishingiz mumkin.\n\n"
        f"Quyidagi tugmalardan birini tanlang:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ============================================
# Tugma bosilganda ishlaydigan funksiyalar
# ============================================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # Paketlar ro'yxati
    if data == "packages":
        text = "📦 *DONATE PAKETLARI*\n\n"
        for key, pkg in DONATE_PACKAGES.items():
            text += f"{pkg['name']} — *{pkg['price']}* ({pkg['duration']})\n"
            text += f"{pkg['perks']}\n\n"
        
        keyboard = [[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    # Server ma'lumoti
    elif data == "server_info":
        text = (
            f"🖥️ *SERVER MA'LUMOTI*\n\n"
            f"🌐 IP: `{SERVER_IP}`\n"
            f"🔌 Port: `{SERVER_PORT}`\n"
            f"🎮 Versiya: 1.8 - 1.20\n"
            f"🌍 Rejim: Survival / Kitpvp\n\n"
            f"Serverga ulanish uchun yuqoridagi IP ni ko'chiring!"
        )
        keyboard = [[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    # Yordam
    elif data == "help":
        text = (
            "📞 *YORDAM*\n\n"
            "Muammo yuzaga kelsa admin bilan bog'laning:\n"
            "@admin_username\n\n"
            "Ishlash vaqti: 09:00 - 22:00"
        )
        keyboard = [[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    # Donate sotib olish
    elif data == "donate":
        keyboard = []
        for key, pkg in DONATE_PACKAGES.items():
            keyboard.append([InlineKeyboardButton(
                f"{pkg['name']} — {pkg['price']}", 
                callback_data=f"buy_{key}"
            )])
        keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back_main")])
        
        await query.edit_message_text(
            "🛒 *PAKET TANLANG:*\n\nQaysi paketni sotib olmoqchisiz?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    # Paket tanlandi
    elif data.startswith("buy_"):
        pkg_key = data.replace("buy_", "")
        pkg = DONATE_PACKAGES[pkg_key]
        
        user_orders[query.from_user.id] = {"package": pkg_key}
        context.user_data["selected_package"] = pkg_key
        
        text = (
            f"✅ Siz tanlagan paket: *{pkg['name']}*\n"
            f"💰 Narx: *{pkg['price']}*\n"
            f"⏳ Muddat: {pkg['duration']}\n\n"
            f"📝 Iltimos, Minecraft *nickname*ingizni yuboring:"
        )
        await query.edit_message_text(text, parse_mode='Markdown')
        return WAITING_NICKNAME
    
    # To'lov usuli tanlandi
    elif data.startswith("pay_"):
        method_key = data.replace("pay_", "")
        user_id = query.from_user.id
        
        if user_id in user_orders:
            user_orders[user_id]["payment"] = method_key
        
        pkg_key = context.user_data.get("selected_package")
        pkg = DONATE_PACKAGES[pkg_key]
        
        text = (
            f"💳 *TO'LOV USULI: {PAYMENT_METHODS[method_key]}*\n\n"
            f"Paket: {pkg['name']}\n"
            f"Narx: *{pkg['price']}*\n\n"
            f"📤 To'lov ma'lumoti:\n`{PAYMENT_DETAILS[method_key]}`\n\n"
            f"⚠️ *Muhim:* To'lovni amalga oshirgandan so'ng, "
            f"to'lov chekini (screenshot) shu yerga yuboring. "
            f"Admin tekshirib, 5-10 daqiqa ichida rank beriladi!"
        )
        await query.edit_message_text(text, parse_mode='Markdown')
        return WAITING_PAYMENT_PROOF
    
    # Asosiy menuga qaytish
    elif data == "back_main":
        keyboard = [
            [InlineKeyboardButton("🛒 Donate Sotib Olish", callback_data="donate")],
            [InlineKeyboardButton("📋 Paketlar Ro'yxati", callback_data="packages")],
            [InlineKeyboardButton("🖥️ Server Ma'lumoti", callback_data="server_info")],
            [InlineKeyboardButton("📞 Yordam", callback_data="help")],
        ]
        await query.edit_message_text(
            f"🎮 *HEROMINE DONATE BOT*\n\nQuyidagi tugmalardan birini tanlang:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

# ============================================
# Nickname qabul qilish
# ============================================
async def receive_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nickname = update.message.text
    user_id = update.from_user.id
    
    if user_id in user_orders:
        user_orders[user_id]["nickname"] = nickname
    
    context.user_data["nickname"] = nickname
    
    keyboard = []
    for key, name in PAYMENT_METHODS.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"pay_{key}")])
    
    await update.message.reply_text(
        f"✅ Nickname saqlandi: *{nickname}*\n\n"
        f"💳 To'lov usulini tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return WAITING_PAYMENT_PROOF

# ============================================
# To'lov chekini qabul qilish
# ============================================
async def receive_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.from_user.id
    user = update.from_user
    
    pkg_key = context.user_data.get("selected_package", "unknown")
    nickname = context.user_data.get("nickname", "unknown")
    pkg = DONATE_PACKAGES.get(pkg_key, {"name": "Unknown", "price": "Unknown"})
    
    # Adminga xabar yuborish
    caption = (
        f"🆕 *YANGI DONATE SO'ROVI!*\n\n"
        f"👤 Foydalanuvchi: {user.first_name} (@{user.username or 'username yoq'})\n"
        f"🆔 ID: `{user_id}`\n"
        f"🎮 Nickname: `{nickname}`\n"
        f"📦 Paket: {pkg['name']}\n"
        f"💰 Narx: {pkg['price']}\n\n"
        f"✅ Tasdiqlash uchun quyidagi komandadan foydalaning:\n"
        f"`/confirm {user_id} {pkg_key} {nickname}`"
    )
    
    try:
        if update.message.photo:
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=update.message.photo[-1].file_id,
                caption=caption,
                parse_mode='Markdown'
            )
        elif update.message.document:
            await context.bot.send_document(
                chat_id=ADMIN_ID,
                document=update.message.document.file_id,
                caption=caption,
                parse_mode='Markdown'
            )
        else:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=caption + f"\n\n📝 Xabar: {update.message.text}",
                parse_mode='Markdown'
            )
    except Exception as e:
        logging.error(f"Admin ga yuborishda xato: {e}")
    
    # Foydalanuvchiga javob
    await update.message.reply_text(
        f"✅ *So'rovingiz qabul qilindi!*\n\n"
        f"Paket: {pkg['name']}\n"
        f"Nickname: `{nickname}`\n\n"
        f"⏳ Admin tekshirib, *5-10 daqiqa* ichida rankingiz beriladi!\n"
        f"Savollar bo'lsa: /help",
        parse_mode='Markdown'
    )
    
    return ConversationHandler.END

# ============================================
# Admin buyruqlari
# ============================================
async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Siz admin emassiz!")
        return
    
    try:
        args = context.args
        if len(args) < 3:
            await update.message.reply_text(
                "❌ Format: `/confirm USER_ID PAKET NICKNAME`\n"
                "Misol: `/confirm 123456789 vip Steve`",
                parse_mode='Markdown'
            )
            return
        
        user_id = int(args[0])
        pkg_key = args[1]
        nickname = args[2]
        pkg = DONATE_PACKAGES.get(pkg_key, {"name": pkg_key})
        
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"🎉 *TABRIKLAYMIZ!*\n\n"
                f"Sizning donate so'rovingiz tasdiqlandi!\n\n"
                f"📦 Paket: *{pkg['name']}*\n"
                f"🎮 Nickname: `{nickname}`\n\n"
                f"Serverga kiring va rankingizni tekshiring!\n"
                f"🌐 IP: `{SERVER_IP}`"
            ),
            parse_mode='Markdown'
        )
        
        await update.message.reply_text(
            f"✅ *{nickname}* ga *{pkg['name']}* paketi tasdiqlandi va foydalanuvchiga xabar yuborildi!",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi. /start bosing.")
    return ConversationHandler.END

# ============================================
# BOTNI ISHGA TUSHIRISH
# ============================================
def main():
    print("🤖 HEROMINE Donate Bot ishga tushmoqda...")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^buy_")],
        states={
            WAITING_NICKNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_nickname)],
            WAITING_PAYMENT_PROOF: [
                MessageHandler(filters.PHOTO | filters.Document.ALL | filters.TEXT & ~filters.COMMAND, receive_payment_proof),
                CallbackQueryHandler(button_handler, pattern="^pay_")
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("confirm", confirm_payment))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("✅ Bot muvaffaqiyatli ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
