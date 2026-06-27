import os
import asyncio
import datetime

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from db import init_db, add_user, get_channel, add_referral


# ---------------- ENV ----------------
ADMIN_ID = int(os.getenv("ADMIN_ID", "7983838654"))
BOT_TOKEN = os.getenv("BOT_TOKEN")


# ---------------- INIT ----------------
async def post_init(app: Application):
    await init_db()
    print("✅ Database initialized")


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    await add_user(user_id, str(datetime.datetime.utcnow()))
    await add_referral(user_id)

    keyboard = [
        [KeyboardButton("➕ Add Bot"), KeyboardButton("🗑 Delete Bot")],
        [KeyboardButton("🤖 My Bots")]
    ]

    if user_id == ADMIN_ID:
        keyboard.append([KeyboardButton("⚙ Admin Panel")])

    await update.message.reply_text(
        "👋 Welcome to Creatmenu Bot System\n"
        "Manage your bots easily.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# ---------------- CHANNEL CHECK ----------------
async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    channel = await get_channel()

    if not channel:
        return True

    try:
        member = await context.bot.get_chat_member(channel, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
        return False
    except:
        return True


# ---------------- MESSAGE HANDLER ----------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    # FORCE JOIN SYSTEM
    ok = await check_join(update, context, user_id)
    if not ok:
        channel = await get_channel()
        await update.message.reply_text(
            f"⚠ Please join our channel first:\n{channel}"
        )
        return

    # BASIC MENU ROUTES
    if text == "➕ Add Bot":
        await update.message.reply_text("📩 Send your bot token to add bot...")
        return

    if text == "🗑 Delete Bot":
        await update.message.reply_text("🗑 Send bot ID to delete...")
        return

    if text == "🤖 My Bots":
        await update.message.reply_text("📊 Loading your bots...")
        return

    if text == "⚙ Admin Panel" and user_id == ADMIN_ID:
        await update.message.reply_text("⚙ Admin Panel opening...")
        return

    await update.message.reply_text("❌ DON'T UNDERSTAND")


# ---------------- MAIN ----------------
def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not set in Railway environment variables")
        return

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
