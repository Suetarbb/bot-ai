import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_API_KEY_2 = os.getenv("CLAUDE_API_KEY_2")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

PLANS = {
    "free":  {"messages": 10,   "price": 0,    "name": "🆓 Бесплатный"},
    "basic": {"messages": 100,  "price": 29900,"name": "⭐ Базовый"},
    "pro":   {"messages": 1000, "price": 79900,"name": "🚀 Легенда"},
    "mega":  {"messages": 2500, "price": 148800,"name": "👾 ULTIMATE"},
}
UNSPLASH_KEY = "mkwJDXEVDpZ3rJJGnodocXWc3caHGZuzhxWWtuC6OP8"