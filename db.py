import aiosqlite

DB_NAME = "bot.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            joined_at TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS bots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            token TEXT,
            bot_username TEXT,
            is_banned INTEGER DEFAULT 0,
            created_at TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_username TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            user_id INTEGER PRIMARY KEY,
            invited_count INTEGER DEFAULT 0,
            unlocked_bots INTEGER DEFAULT 0
        )
        """)

        await db.commit()


# USERS
async def add_user(user_id, joined_at):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id, joined_at) VALUES (?,?)",
                         (user_id, joined_at))
        await db.commit()


# BOTS
async def add_bot(user_id, token, username, created_at):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT INTO bots (user_id, token, bot_username, created_at)
        VALUES (?,?,?,?)
        """, (user_id, token, username, created_at))
        await db.commit()


async def get_user_bots(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT * FROM bots WHERE user_id=?", (user_id,))
        return await cursor.fetchall()


async def delete_bot(bot_id, user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM bots WHERE id=? AND user_id=?", (bot_id, user_id))
        await db.commit()


# BAN SYSTEM
async def ban_bot(bot_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE bots SET is_banned=1 WHERE id=?", (bot_id,))
        await db.commit()


async def unban_bot(bot_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE bots SET is_banned=0 WHERE id=?", (bot_id,))
        await db.commit()


# CHANNEL SETTINGS
async def set_channel(username):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM channels")
        await db.execute("INSERT INTO channels (channel_username) VALUES (?)", (username,))
        await db.commit()


async def get_channel():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT channel_username FROM channels LIMIT 1")
        row = await cursor.fetchone()
        return row[0] if row else None


# REFERRALS (invite system)
async def add_referral(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT OR IGNORE INTO referrals (user_id, invited_count, unlocked_bots)
        VALUES (?,0,0)
        """, (user_id,))
        await db.commit()


async def increase_referral(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        UPDATE referrals
        SET invited_count = invited_count + 1
        WHERE user_id=?
        """, (user_id,))
        await db.commit()


async def get_referral(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT * FROM referrals WHERE user_id=?", (user_id,))
        return await cursor.fetchone()
