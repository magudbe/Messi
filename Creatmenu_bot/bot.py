import os
import datetime
import asyncio
import aiosqlite

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

from db import init_db, add_user, get_channel, add_referral, set_channel, DB_NAME


# ================= ENV =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7983838654"))


# ================= INIT =================
async def post_init(app: Application):
    await init_db()
    print("✅ DB initialized")


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    await add_user(user_id, str(datetime.datetime.utcnow()))
    await add_referral(user_id)

    keyboard = [
        [KeyboardButton("➕ Add Bot"), KeyboardButton("🗑 Delete Bot")],
        [KeyboardButton("🤖 My Bots")]
    ]

    if user_id == ADMIN_ID:
        keyboard.append([KeyboardButton("⚙ Admin Panel")])

    await update.message.reply_text(
        "👋 Welcome to Creatmenu Bot System",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# ================= FORCE JOIN =================
async def check_join(context, user_id):
    channel = await get_channel()

    if not channel:
        return True

    try:
        member = await context.bot.get_chat_member(channel, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return True


# ================= DB HELPERS =================
async def get_stats():
    async with aiosqlite.connect(DB_NAME) as db:
        users = await (await db.execute("SELECT COUNT(*) FROM users")).fetchone()
        bots = await (await db.execute("SELECT COUNT(*) FROM bots")).fetchone()
        banned = await (await db.execute("SELECT COUNT(*) FROM bots WHERE is_banned=1")).fetchone()

        return users[0], bots[0], banned[0]


# ================= ADMIN PANEL =================
async def admin_panel(update, context):
    keyboard = [
        [KeyboardButton("📊 Stats"), KeyboardButton("📢 Broadcast")],
        [KeyboardButton("📡 Channel Post"), KeyboardButton("🗑 Delete Channel Post")],
        [KeyboardButton("🚫 Ban Bot"), KeyboardButton("✅ Unban Bot")],
        [KeyboardButton("⬅ Back")]
    ]

    await update.message.reply_text(
        "⚙ Admin Panel",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# ================= MAIN HANDLER =================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    # FORCE JOIN
    if not await check_join(context, user_id):
        channel = await get_channel()
        await update.message.reply_text(f"⚠ Join first: {channel}")
        return

    # ================= USER MENU =================
    if text == "➕ Add Bot":
        await update.message.reply_text("📩 Send bot token")
        return

    if text == "🗑 Delete Bot":
        await update.message.reply_text("🗑 Send bot ID")
        return

    if text == "🤖 My Bots":
        await update.message.reply_text("📊 Loading bots...")
        return

    # ================= ADMIN OPEN =================
    if text == "⚙ Admin Panel" and user_id == ADMIN_ID:
        await admin_panel(update, context)
        return

    # ================= ADMIN ACTIONS =================
    if user_id == ADMIN_ID:

        if text == "📊 Stats":
            users, bots, banned = await get_stats()
            await update.message.reply_text(
                f"📊 STATS\nUsers: {users}\nBots: {bots}\nBanned: {banned}"
            )
            return

        if text == "📡 Channel Post":
            await update.message.reply_text("Send channel @username")
            return

        if text == "🗑 Delete Channel Post":
            await set_channel("")
            await update.message.reply_text("🗑 Channel removed")
            return

        if text == "🚫 Ban Bot":
            await update.message.reply_text("Send: BAN <id>")
            return

        if text == "✅ Unban Bot":
            await update.message.reply_text("Send: UNBAN <id>")
            return

        if text.startswith("@"):
            await set_channel(text)
            await update.message.reply_text(f"📡 Channel set {text}")
            return

        if text.startswith("BAN "):
            bot_id = int(text.split()[1])
            async with aiosqlite.connect(DB_NAME) as db:
                await db.execute("UPDATE bots SET is_banned=1 WHERE id=?", (bot_id,))
                await db.commit()
            await update.message.reply_text("🚫 Banned")
            return

        if text.startswith("UNBAN "):
            bot_id = int(text.split()[1])
            async with aiosqlite.connect(DB_NAME) as db:
                await db.execute("UPDATE bots SET is_banned=0 WHERE id=?", (bot_id,))
                await db.commit()
            await update.message.reply_text("✅ Unbanned")
            return

    # ================= DEFAULT =================
    await update.message.reply_text("❌ DON'T UNDERSTAND")


# ================= MAIN =================
def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN missing")
        return

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
