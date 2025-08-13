from aiogram import Router, types
from app.services.movies import fetch_movies

router = Router()

@router.message(lambda m: m.text.lower() in ["кино", "/kino"])
async def send_movies(message: types.Message):
    movies = await fetch_movies()
    if not movies:
        await message.answer("⚠️ Сейчас нет данных о сеансах. Попробуйте позже.")
        return

    text_parts = []
    for mdata in movies:
        movie_block = (
            f"🎬 <b>{mdata['title']}</b>
"
            f"📌 Жанр: {mdata['categories']}
"
            f"🌍 {mdata['details']}
"
            f"🕒 Сеансы: {', '.join(mdata['times']) if mdata['times'] else 'Нет данных'}"
        )
        text_parts.append(movie_block)

    full_text = "\n\n".join(text_parts)
    await message.answer(full_text, parse_mode="HTML")
