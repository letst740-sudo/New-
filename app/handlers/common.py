from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from app.keyboards import (
    back_only_inline, main_kb, gender_kb, weather_inline, vk_only_inline, tg_only_inline, contact_inline,
    BTN_WEATHER, BTN_MOVIES, BTN_TRANSP, BTN_RATES, BTN_NEWS_VK, BTN_NEWS_TG, BTN_CONTACT, BTN_AI, BTN_CONTACTS_CITY
)
from app.states import RegStates
from app.storage import upsert_user, get_user, log_event
from app.services import weather as W
from app.services import rates as R
from app.services import movies as M
from app.config import settings

router = Router()

# Мягкое удаление пользовательских сообщений, чтобы не было флуда
import asyncio
async def _del_after(msg: Message, delay: float = 0.9):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception:
        pass


# -------------------- Регистрация / старт --------------------
@router.message(CommandStart())
async def start(m: Message, state: FSMContext):
    user = await get_user(m.from_user.id)
    if user:
        # Уже зарегистрирован — показываем главное меню
        await _del_after(m)
        return await m.answer("Главное меню:", reply_markup=main_kb())

    nickname = m.from_user.username and ("@" + m.from_user.username) or (m.from_user.first_name or "Гость")
    await state.update_data(nickname=nickname[:64])
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"📝 Зарегистрироваться как {nickname}", callback_data="reg:start")]
    ])
    await _del_after(m)
    await m.answer(
        "<b>👋 Добро пожаловать в <u>MarksCity</u>!</b>\n\n"
        "<em>Городской помощник: погода, кино, транспорт, курсы и ИИ.</em>\n\n"
        "Нажмите кнопку ниже, чтобы пройти быструю регистрацию.",
        reply_markup=kb,
        parse_mode="HTML",
    )


@router.callback_query(F.data == "reg:start")
async def reg_start(c: CallbackQuery, state: FSMContext):
    await state.set_state(RegStates.ASK_GENDER)
    await c.message.edit_text("<b>Пол</b> — выберите вариант ниже:", reply_markup=gender_kb(), parse_mode="HTML")


@router.callback_query(F.data.startswith("gender:"), RegStates.ASK_GENDER)
async def set_gender(c: CallbackQuery, state: FSMContext):
    gender = "Мужской" if c.data.endswith("M") else "Женский"
    await state.update_data(gender=gender)
    await state.set_state(RegStates.ASK_AGE)
    data = await state.get_data()
    nick = data.get("nickname") or (c.from_user.username and ("@" + c.from_user.username)) or (c.from_user.first_name or "—")
    await c.message.edit_text(
        f"<b>Ваш ник:</b> {nick}\n<b>Пол:</b> {gender}\nТеперь укажите <b>возраст</b>:",
        reply_markup=None,
        parse_mode="HTML",
    )


@router.message(RegStates.ASK_AGE)
async def set_age(m: Message, state: FSMContext):
    try:
        age = int(m.text.strip())
        if age <= 0:
            raise ValueError
    except Exception:
        return await m.answer("Возраст должен быть числом. Попробуйте ещё раз.")

    data = await state.get_data()
    nick = data.get("nickname") or (m.from_user.username and ("@" + m.from_user.username)) or (m.from_user.first_name or "—")
    gender = data.get("gender", "Мужской")
    await upsert_user(m.from_user.id, nick, gender, age)
    await state.clear()
    await _del_after(m)
    await m.answer("<b>Готово!</b> Выбирайте раздел на клавиатуре ниже 👇", reply_markup=main_kb(), parse_mode="HTML")


# -------------------- Разделы --------------------
@router.message(F.text == BTN_NEWS_VK)
async def news_vk(m: Message):
    await _del_after(m)
    await m.answer(
        "<b>📰 Самые свежие и важные новости — теперь в нашем VK!</b>",
        reply_markup=vk_only_inline(settings.vk_url),
        parse_mode="HTML",
    )


@router.message(F.text == BTN_NEWS_TG)
async def news_tg(m: Message):
    await _del_after(m)
    await m.answer(
        "<b>📢 Всё, что важно знать, уже ждёт вас в TG!</b>",
        reply_markup=tg_only_inline(settings.tg_url),
        parse_mode="HTML",
    )


@router.message(F.text == BTN_CONTACT)
async def contact(m: Message):
    await _del_after(m)
    await m.answer(
        "<b>📮 Связаться с администратором</b>",
        reply_markup=contact_inline("https://vk.com/yodatox", "@Listen_mp4"),
        parse_mode="HTML",
    )


@router.message(F.text == BTN_WEATHER)
async def weather(m: Message):
    await _del_after(m)
    await log_event(m.from_user.id, "weather")
    user = await get_user(m.from_user.id)

    data = await W.get_weather_cached()
    cur = data.get("current", {})

    t = cur.get("temperature_2m")
    tfeels = cur.get("apparent_temperature")
    wind = cur.get("wind_speed_10m", 0.0) or 0.0
    rain = cur.get("precipitation", 0.0) or 0.0

    gender = (user["gender"] if user else "Мужской")
    try:
        t_f = float(t) if t is not None else 0.0
        tf_f = float(tfeels) if tfeels is not None else t_f
        w_f = float(wind)
        r_f = float(rain)
    except Exception:
        t_f = tf_f = w_f = r_f = 0.0

    advice = W.outfit_advice(t_f, w_f, r_f, gender)
    text = (
        "🌤 <b>Погода в Марксе</b>\n\n"
        f"🌡 Температура: <b>{t_f:.0f}°C</b> (ощущается: {tf_f:.0f}°C)\n"
        f"💨 Ветер: <b>{w_f:.0f} м/с</b>\n"
        f"🌧 Осадки: <b>{r_f} мм</b>\n\n"
        f"👕 <i>Совет ({gender[:1]})</i>: {advice}"
    )
    await m.answer(text, reply_markup=weather_inline(), parse_mode="HTML")


@router.callback_query(F.data == "weather:refresh")
async def weather_refresh(c: CallbackQuery):
    try:
        await W.fetch_weather()
        await c.answer("Обновлено", show_alert=False)
    except Exception:
        await c.answer("Пока показываю кэш.", show_alert=False)
    # Перерисуем карточку погоды:
    m = Message.model_construct(**c.message.model_dump())
    await weather(m)


@router.message(F.text == BTN_RATES)
async def rates(m: Message):
    await _del_after(m)
    await log_event(m.from_user.id, "rates")

    fiat, crypto = await R.get_rates_cached()
    rates_map = fiat.get("rates", {})
    try:
        usd_val = float(rates_map.get("USD")) if rates_map.get("USD") else None
        eur_val = float(rates_map.get("EUR")) if rates_map.get("EUR") else None
        usd_rub = (1 / usd_val) if usd_val and usd_val > 0 else None
        eur_rub = (1 / eur_val) if eur_val and eur_val > 0 else None
    except Exception:
        usd_rub = eur_rub = None

    btc = crypto.get("bitcoin", {}).get("usd")
    ton = crypto.get("toncoin", {}).get("usd")
    eth = crypto.get("ethereum", {}).get("usd")

    text = "💱 <b>Курсы</b>\n"
    text += f"USD: {usd_rub:.2f} ₽\n" if usd_rub else "USD: —\n"
    text += f"EUR: {eur_rub:.2f} ₽\n" if eur_rub else "EUR: —\n"
    text += f"BTC: {btc:.2f} $\n" if btc else "BTC: —\n"
    text += f"TON: {ton:.2f} $\n" if ton else "TON: —\n"
    text += f"ETH: {eth:.2f} $\n" if eth else "ETH: —\n"
    await m.answer(text, reply_markup=back_only_inline(), parse_mode="HTML")


@router.message(F.text == BTN_MOVIES)
async def movies(m: Message):
    await _del_after(m)
    await log_event(m.from_user.id, "cinema")
    try:
        items = await M.fetch_movies()
    except Exception:
        items = []

    if not items:
        return await m.answer("⚠️ Сейчас нет данных о сеансах. Попробуйте позже.", reply_markup=back_only_inline())

    CLOCK = "\U0001F552"
    parts = []
    for it in items[:12]:
        title = it.get("title", "")
        times = ", ".join(it.get("times") or [])
        parts.append(f"🎬 <b>{title}</b>\n{CLOCK} {times if times else 'нет данных'}")

    await m.answer("🎬 <b>Сеансы сегодня</b>\n\n" + "\n\n".join(parts), reply_markup=back_only_inline(), parse_mode="HTML")


@router.message(F.text == BTN_TRANSP)
async def transport(m: Message):
    await _del_after(m)
    await log_event(m.from_user.id, "transport")
    await m.answer(
        "Импортируйте расписание CSV в <code>data/transport.csv</code> "
        "(в разработке загрузка из админки).",
        reply_markup=back_only_inline(),
        parse_mode="HTML",
    )


@router.message(F.text == BTN_AI)
async def ai_intro(m: Message):
    await _del_after(m)
    await m.answer(
        "<b>🤖 Нейросеть</b> — задайте вопрос одним сообщением.\n"
        "<i>Для сброса контекста:</i> /ai_reset",
        reply_markup=back_only_inline(),
        parse_mode="HTML",
    )


@router.message(Command("ai_reset"))
async def ai_reset(m: Message):
    await m.answer("Контекст очищен. Пишите новый запрос.", reply_markup=back_only_inline())


# -------------------- Город на связи --------------------
CITY_CONTACTS_TEXT = """
🏛 <b>Администрация</b> 🏛
+7 (84567) 5-55-55 - Приемная главы Марксовского района
+7 (84567) 5-10-02 - Единая диспетчерская служба
+7 (84567) 5-17-80 - Комитет образования
+7 (84567) 5-13-04 - Комитет культуры спорта и молодежной политики
+7 (84567) 5-18-35 - Комитет строительства благоустройства и дорожного хозяйства

🏥 <b>Больница</b> 🏥
☎️ Приёмная главного врача ГУЗ СО "Марксовская РБ" — +79020422444
☎️ Приёмная поликлиники — +79003148548
☎️ Приёмная детской поликлиники — +79003149510
☎️ Заместитель главного врача по лечебной работе — +79018208666
☎️ Заместитель главного врача по экспертизе временной нетрудоспособности — 8 84567 5‑39‑60

☎️ Акушерское отделение (стационар) — 8 84567 5‑49‑20
☎️ Бак. лаборатория — 8 84567 5‑43‑25

☎️ Бухгалтерия
• Главный бухгалтер — +79018209222
• Материальный стол — +79003149446, +79003149450
• Финансовый отдел — +79003149483
• Расчётный отдел — +79003149489

☎️ Гинекологическое отделение (стационар) — 8 84567 5‑53‑40
☎️ Гражданская оборона — +79003145963
☎️ Детское отделение (стационар) — 8 84567 5‑47‑71
☎️ Женская консультация (поликлиника) — +79003147902
☎️ Инфекционное отделение (стационар) — 8 84567 5‑57‑11
☎️ Клинико‑диагностическая лаборатория (стационар) — 8 84567 5‑46‑20
☎️ Компьютерная томография (КТ) — +79271024597
☎️ Отдел закупок — +79003103888

☎️ Отдел кадров
• Начальник — +79962008111
• Специалисты — +79003147848, +79003147863

☎️ Охрана труда — +79003145963
☎️ Приёмное отделение (стационар) — +79003145664
☎️ Реанимационное отделение (стационар) — 8 84567 5‑39‑85
☎️ Регистратура поликлиники — +79003105444
☎️ Регистратура детской поликлиники — +79020433888
☎️ Справки о смерти — +79003148382
☎️ Терапевтическое отделение (стационар) — 8 84567 5‑49‑40
☎️ Флюорография (поликлиника) — 8 84567 5‑59‑84
☎️ Хирургическое отделение (стационар) — 8 84567 5‑39‑80
☎️ Хозяйственный отдел (стационар) — 8 84567 5‑45‑21
☎️ Экономический отдел — +79003145668
☎️ Юрисконсульт — +79003149442
"""

@router.message(F.text == BTN_CONTACTS_CITY)
async def city_contacts_handler(m: Message):
    await _del_after(m)
    await m.answer(CITY_CONTACTS_TEXT, parse_mode="HTML", reply_markup=back_only_inline())


# -------------------- Возврат в меню --------------------
@router.callback_query(F.data == "menu:back")
async def back_to_menu(c: CallbackQuery):
    try:
        await c.message.delete()
    except Exception:
        pass
    await c.message.answer("Главное меню:", reply_markup=main_kb())
    await c.answer()