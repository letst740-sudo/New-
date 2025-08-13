from aiohttp import ClientSession
from bs4 import BeautifulSoup
from typing import List, Dict
from app.storage import cache_get, cache_set

KINOAFISHA_URL = "https://marks.kinoafisha.info/cinema/8325680/schedule"

async def fetch_movies() -> List[Dict]:
    # Проверяем кэш
    cached = await cache_get("movies_list")
    if cached:
        return cached.get("items", [])

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0.0.0 Safari/537.36"
    }

    async with ClientSession() as session:
        async with session.get(KINOAFISHA_URL, headers=headers, timeout=12) as resp:
            resp.raise_for_status()
            html = await resp.text()

    soup = BeautifulSoup(html, "html.parser")
    schedule_container = soup.find("div", class_="schedule_showtimes")
    if not schedule_container:
        await cache_set("movies_list", {"items": []})
        return []

    items: List[Dict] = []
    movie_items = schedule_container.find_all("div", class_="showtimes_item")

    for item in movie_items:
        if "showtimes_item-row" in item.get("class", []):
            continue

        movie_info_div = item.find("div", class_="showtimesMovie_info")
        movie_title = "Название не найдено"
        movie_categories = ""
        movie_details = ""

        if movie_info_div:
            title_span = movie_info_div.find("span", class_="showtimesMovie_name")
            if title_span:
                movie_title = title_span.text.strip()
            categories_span = movie_info_div.find("span", class_="showtimesMovie_categories")
            if categories_span:
                movie_categories = categories_span.text.strip()
            details_span = movie_info_div.find("span", class_="showtimesMovie_details")
            if details_span:
                movie_details = details_span.text.strip()

        # Сеансы
        showtimes_list = []
        sessions_container = item.find("div", class_="showtimes_sessions")
        if sessions_container:
            session_times = sessions_container.find_all("span", class_="session_time")
            showtimes_list = [time.text.strip() for time in session_times]

        items.append({
            "title": movie_title,
            "categories": movie_categories,
            "details": movie_details,
            "times": showtimes_list
        })

    # Кэшируем результат
    await cache_set("movies_list", {"items": items})
    return items
