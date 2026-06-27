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

from telegram import ReplyKeyboardMarkup, KeyboardButton


# ---------------- ADMIN PANEL ----------------
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        return

    keyboard = [
        [KeyboardButton("📊 Stats"), KeyboardButton("📢 Broadcast")],
        [KeyboardButton("📢 Broadcast Main Bot")],
        [KeyboardButton("📡 Channel Post"), KeyboardButton("🗑 Delete Channel Post")],
        [KeyboardButton("🚫 Ban Bot"), KeyboardButton("✅ Unban Bot")],
        [KeyboardButton("⬅ Back")]
    ]

    await update.message.reply_text(
        "⚙ Admin Panel",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# ---------------- ADMIN ACTION ROUTER ----------------
async def admin_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        return

    # BACK
    if text == "⬅ Back":
        await start(update, context)
        return

    # STATS (simple version for now)
    if text == "📊 Stats":
        await update.message.reply_text(
            "📊 System Stats:\n"
            "- Users: loading...\n"
            "- Bots: loading...\n"
            "- Videos: loading...\n"
        )
        return

    # BROADCAST
    if text == "📢 Broadcast":
        await update.message.reply_text(
            "📢 Send message / media to broadcast to ALL bots users."
        )
        return

    # MAIN BOT BROADCAST
    if text == "📢 Broadcast Main Bot":
        await update.message.reply_text(
            "📢 Send message for MAIN bot users only."
        )
        return

    # CHANNEL POST
    if text == "📡 Channel Post":
        await update.message.reply_text(
            "📡 Send channel username (e.g @channel)"
        )
        return

    if text == "🗑 Delete Channel Post":
        await update.message.reply_text(
            "🗑 Channel restriction removed."
        )
        return

    # BAN / UNBAN PLACEHOLDER
    if text == "🚫 Ban Bot":
        await update.message.reply_text(
            "🚫 Send Bot ID to ban"
        )
        return

    if text == "✅ Unban Bot":
        await update.message.reply_text(
            "✅ Send Bot ID to unban"
        )
        return

import aiosqlite
from db import DB_NAME, set_channel, get_channel


# ---------------- REAL STATS ----------------
async def get_stats():
    async with aiosqlite.connect(DB_NAME) as db:

        users = await (await db.execute("SELECT COUNT(*) FROM users")).fetchone()
        bots = await (await db.execute("SELECT COUNT(*) FROM bots")).fetchone()
        banned = await (await db.execute("SELECT COUNT(*) FROM bots WHERE is_banned=1")).fetchone()

        return {
            "users": users[0],
            "bots": bots[0],
            "banned": banned[0]
        }


# ---------------- BAN / UNBAN ----------------
async def ban_unban_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text.startswith("BAN "):
        try:
            bot_id = int(text.split(" ")[1])
            async with aiosqlite.connect(DB_NAME) as db:
                await db.execute("UPDATE bots SET is_banned=1 WHERE id=?", (bot_id,))
                await db.commit()

            await update.message.reply_text("🚫 Bot banned successfully")
        except:
            await update.message.reply_text("❌ Invalid bot ID")

        return True

    if text.startswith("UNBAN "):
        try:
            bot_id = int(text.split(" ")[1])
            async with aiosqlite.connect(DB_NAME) as db:
                await db.execute("UPDATE bots SET is_banned=0 WHERE id=?", (bot_id,))
                await db.commit()

            await update.message.reply_text("✅ Bot unbanned successfully")
        except:
            await update.message.reply_text("❌ Invalid bot ID")

        return True

    return False


# ---------------- CHANNEL SET / DELETE ----------------
async def channel_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text.startswith("@"):
        await set_channel(text)
        await update.message.reply_text(f"📡 Channel set: {text}")
        return True

    if text == "DELETE CHANNEL":
        await set_channel("")
        await update.message.reply_text("🗑 Channel removed")
        return True

    return False


# ---------------- BROADCAST CORE (PLACEHOLDER READY) ----------------
async def broadcast_all(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
    async with aiosqlite.connect(DB_NAME) as db:
        users = await db.execute("SELECT user_id FROM users")
        rows = await users.fetchall()

        for row in rows:
            try:
                await context.bot.send_message(chat_id=row[0], text=message)
            except:
                pass

    await update.message.reply_text("📢 Broadcast sent to all users")


# ---------------- ADMIN STATS DISPLAY ----------------
async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = await get_stats()

    text = f"""
📊 SYSTEM STATS

👥 Users: {stats['users']}
🤖 Bots: {stats['bots']}
🚫 Banned Bots: {stats['banned']}
"""

    await update.message.reply_text(text)


# ---------------- INTEGRATION HOOK (ADD TO ROUTER) ----------------
async def admin_extra_routes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Add this into handle_message BEFORE default response
    """

    if await ban_unban_router(update, context):
        return True

    if await channel_router(update, context):
        return True

    if update.message.text == "📊 Stats":
        await show_stats(update, context)
        return True

    return False


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
