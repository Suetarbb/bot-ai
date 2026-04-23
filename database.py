import aiosqlite
import datetime

DB_PATH = "bot_database.db"

# ===================== ДОСТИЖЕНИЯ =====================
ACHIEVEMENTS = {
    "first_step":    {"emoji": "🌱", "name": "Первый шаг",     "desc": "Первое действие в боте",        "cat": "📊 Активность"},
    "consistent":    {"emoji": "🔥", "name": "Постоянный",      "desc": "7 дней подряд в боте",          "cat": "📊 Активность"},
    "veteran":       {"emoji": "🏛",  "name": "Ветеран",         "desc": "30 дней с регистрации",         "cat": "📊 Активность"},
    "slide_master":  {"emoji": "🎓", "name": "Мастер слайдов",  "desc": "10 презентаций создано",        "cat": "🎨 Презентации"},
    "collector":     {"emoji": "🎨", "name": "Коллекционер",    "desc": "Использовал все 5 тем",         "cat": "🎨 Презентации"},
    "night_owl":     {"emoji": "🦉", "name": "Ночная сова",     "desc": "Запрос после полуночи",         "cat": "🌙 Время"},
    "early_bird":    {"emoji": "🐦", "name": "Ранняя пташка",   "desc": "Запрос до 7:00 утра",           "cat": "🌙 Время"},
    "chatterbox":    {"emoji": "💬", "name": "Болтун",          "desc": "50 сообщений боту",             "cat": "💬 Общение"},
    "curious":       {"emoji": "❓", "name": "Почемучка",       "desc": "10 вопросов подряд",            "cat": "💬 Общение"},
    "lucky":         {"emoji": "🍀", "name": "Везунчик",        "desc": "Редкая удача — шанс 1%",        "cat": "🎲 Случайные"},
    "explorer":      {"emoji": "🔍", "name": "Исследователь",   "desc": "Попробовал все команды",        "cat": "🎲 Случайные"},
    "paparazzi":     {"emoji": "📸", "name": "Папарацци",       "desc": "Первое фото боту",              "cat": "📸 Фото"},
    "photo_album":   {"emoji": "🖼",  "name": "Фотоальбом",      "desc": "10 фото боту",                  "cat": "📸 Фото"},
    "instagrammer":  {"emoji": "💫", "name": "Инстаграмер",     "desc": "50 фото боту",                  "cat": "📸 Фото"},
    "week_champion": {"emoji": "🏆", "name": "Чемпион недели",  "desc": "1 место в топе 7 дней подряд", "cat": "👑 Лидерство"},
    "king":          {"emoji": "👑", "name": "Король",          "desc": "Выдано администратором",        "cat": "👑 Лидерство"},
}

# ===================== ИНИЦИАЛИЗАЦИЯ БД =====================
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id        INTEGER PRIMARY KEY,
                username       TEXT,
                plan           TEXT DEFAULT 'free',
                messages_used  INTEGER DEFAULT 0,
                messages_limit INTEGER DEFAULT 10,
                reset_date     TEXT,
                created_at     TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER,
                role       TEXT,
                content    TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                user_id        INTEGER,
                achievement_id TEXT,
                obtained_at    TEXT,
                PRIMARY KEY (user_id, achievement_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id               INTEGER PRIMARY KEY,
                presentations_count   INTEGER DEFAULT 0,
                photos_count          INTEGER DEFAULT 0,
                used_themes           TEXT DEFAULT '',
                streak_days           INTEGER DEFAULT 0,
                last_active           TEXT DEFAULT '',
                consecutive_questions INTEGER DEFAULT 0,
                commands_used         TEXT DEFAULT '',
                top1_days             INTEGER DEFAULT 0,
                last_top1_date        TEXT DEFAULT ''
            )
        """)
        await db.commit()

# ===================== ПОЛЬЗОВАТЕЛИ =====================
async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ) as cursor:
            return await cursor.fetchone()

async def create_user(user_id: int, username: str):
    reset_date = (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT OR IGNORE INTO users 
               (user_id, username, plan, messages_used, messages_limit, reset_date)
               VALUES (?, ?, 'free', 0, 10, ?)""",
            (user_id, username, reset_date)
        )
        await db.commit()
    # создаём запись статистики
    await get_user_stats(user_id)

async def increment_messages(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET messages_used = messages_used + 1 WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()

async def can_send_message(user_id: int) -> bool:
    user = await get_user(user_id)
    if not user:
        return False
    reset_date = datetime.datetime.fromisoformat(user["reset_date"])
    if datetime.datetime.now() > reset_date:
        await reset_user_messages(user_id)
        return True
    return user["messages_used"] < user["messages_limit"]

async def reset_user_messages(user_id: int):
    reset_date = (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET messages_used = 0, reset_date = ? WHERE user_id = ?",
            (reset_date, user_id)
        )
        await db.commit()

async def upgrade_user(user_id: int, plan: str, limit: int):
    reset_date = (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """UPDATE users SET plan = ?, messages_limit = ?, 
               messages_used = 0, reset_date = ? WHERE user_id = ?""",
            (plan, limit, reset_date, user_id)
        )
        await db.commit()

async def add_bonus_messages(user_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET messages_limit = messages_limit + ? WHERE user_id = ?",
            (amount, user_id)
        )
        await db.commit()

# ===================== ИСТОРИЯ =====================
async def save_message(user_id: int, role: str, content: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO conversations (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content)
        )
        await db.commit()

async def get_history(user_id: int, limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT role, content FROM conversations 
               WHERE user_id = ? ORDER BY created_at DESC LIMIT ?""",
            (user_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return list(reversed(rows))

async def clear_history(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM conversations WHERE user_id = ?", (user_id,)
        )
        await db.commit()

# ===================== СТАТИСТИКА =====================
async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT COUNT(*) as total FROM users") as c:
            total = (await c.fetchone())["total"]
        async with db.execute(
            "SELECT COUNT(*) as paid FROM users WHERE plan != 'free'"
        ) as c:
            paid = (await c.fetchone())["paid"]
        return {"total": total, "paid": paid}

async def get_top_users(limit=10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT u.user_id, u.username,
                   u.messages_used,
                   u.plan,
                   COALESCE(s.presentations_count, 0) as pres,
                   COALESCE(s.photos_count, 0) as photos,
                   COUNT(a.achievement_id) as achievements
            FROM users u
            LEFT JOIN user_stats s ON u.user_id = s.user_id
            LEFT JOIN user_achievements a ON u.user_id = a.user_id
            GROUP BY u.user_id
            ORDER BY u.messages_used DESC
            LIMIT ?
        """, (limit,)) as cur:
            return await cur.fetchall()
async def get_weekly_top_user():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT u.user_id, u.username, u.messages_used,
                   COALESCE(s.presentations_count, 0) as pres,
                   COALESCE(s.photos_count, 0) as photos
            FROM users u
            LEFT JOIN user_stats s ON u.user_id = s.user_id
            ORDER BY u.messages_used DESC
            LIMIT 1
        """) as cur:
            return await cur.fetchone()

# ===================== СТАТЫ ПОЛЬЗОВАТЕЛЯ =====================
async def get_user_stats(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM user_stats WHERE user_id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
            if not row:
                await db.execute(
                    "INSERT OR IGNORE INTO user_stats (user_id) VALUES (?)", (user_id,)
                )
                await db.commit()
                async with db.execute(
                    "SELECT * FROM user_stats WHERE user_id = ?", (user_id,)
                ) as cur2:
                    return await cur2.fetchone()
            return row

async def update_user_stats(user_id: int, **kwargs):
    if not kwargs:
        return
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [user_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE user_stats SET {sets} WHERE user_id = ?", vals
        )
        await db.commit()

async def update_streak(user_id: int) -> int:
    stats = await get_user_stats(user_id)
    today = datetime.date.today().isoformat()
    last = stats["last_active"]
    streak = stats["streak_days"] or 0

    if last == today:
        return streak
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    if last == yesterday:
        streak += 1
    else:
        streak = 1

    await update_user_stats(user_id, streak_days=streak, last_active=today)
    return streak

# ===================== ДОСТИЖЕНИЯ =====================
async def give_achievement(user_id: int, achievement_id: str) -> bool:
    """Возвращает True если выдано впервые."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT 1 FROM user_achievements WHERE user_id=? AND achievement_id=?",
            (user_id, achievement_id)
        ) as cur:
            if await cur.fetchone():
                return False
        await db.execute(
            "INSERT INTO user_achievements (user_id, achievement_id, obtained_at) VALUES (?,?,?)",
            (user_id, achievement_id, datetime.datetime.now().isoformat())
        )
        await db.commit()
        return True

async def get_user_achievements(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT achievement_id, obtained_at FROM user_achievements WHERE user_id=? ORDER BY obtained_at",
            (user_id,)
        ) as cur:
            return await cur.fetchall()