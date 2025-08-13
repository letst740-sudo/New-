# app/keyboards.py
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# --- Тексты кнопок ---
BTN_WEATHER = "🌤 Сейчас в Марксе"
BTN_MOVIES  = "🎬 Кино в «Кристалле»"
BTN_TRANSP  = "🚌 Маршруты и рейсы"
BTN_RATES   = "💱 Курс ₽ / ₿"  # константа оставлена для совместимости, в меню кнопку не показываем
BTN_NEWS_VK = "📰 Новости VK"
BTN_NEWS_TG = "📣 Наш Telegram-канал"
BTN_CONTACTS_CITY = "📞 Город на связи"
BTN_CONTACT = "📮 Написать администратору"
BTN_AI      = "🤖 Спросить нейросеть"

# --- Главное меню (без кнопки "Курс") ---
def main_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_WEATHER), KeyboardButton(text=BTN_MOVIES)],
            [KeyboardButton(text=BTN_TRANSP)],
            [KeyboardButton(text=BTN_NEWS_VK)],
            [KeyboardButton(text=BTN_NEWS_TG)],
            [KeyboardButton(text=BTN_CONTACTS_CITY)],  # новая кнопка
            [KeyboardButton(text=BTN_CONTACT), KeyboardButton(text=BTN_AI)],
        ],
        resize_keyboard=True
    )
# --- Клавиатуры, которые импортируются в handlers/common.py ---

def gender_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨 Мужской", callback_data="gender:M")],
        [InlineKeyboardButton(text="👩 Женский", callback_data="gender:F")],
    ])

def weather_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить погоду", callback_data="weather:refresh")],
        [InlineKeyboardButton(text="🔙 Вернуться в меню", callback_data="menu:back")],
    ])

def vk_only_inline(vk_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📰 Открыть VK →", url=vk_url)]
    ])

def tg_only_inline(tg_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📣 Открыть Telegram →", url=tg_url)]
    ])

def contact_inline(vk_url: str, tg_user: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💙 Написать в VK", url=vk_url)],
        [InlineKeyboardButton(text="✉️ Написать в TG", url=f"https://t.me/{tg_user.lstrip('@')}")],
    ])


def back_only_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Вернуться в меню", callback_data="menu:back")]])
