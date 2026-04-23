from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from config import PLANS

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Профиль"),   KeyboardButton(text="💳 Тарифы")],
            [KeyboardButton(text="📊 Презентация"), KeyboardButton(text="❓ Помощь")],
            [KeyboardButton(text="🏆 Достижения"), KeyboardButton(text="📈 Топ")]
        ],
        resize_keyboard=True
    )

def plans_keyboard():
    buttons = []
    for plan_id, plan in PLANS.items():
        if plan_id == "free":
            continue
        buttons.append([
            InlineKeyboardButton(
                text=plan["name"],
                callback_data=f"buy_{plan_id}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)