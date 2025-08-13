from aiohttp import ClientSession
from app.config import settings
from app.storage import cache_get, cache_set

async def fetch_weather():
    url = (f"https://api.open-meteo.com/v1/forecast?latitude={settings.weather_lat}"
           f"&longitude={settings.weather_lon}&current=temperature_2m,apparent_temperature,precipitation,wind_speed_10m&timezone=auto")
    async with ClientSession() as s:
        async with s.get(url, timeout=10) as r:
            r.raise_for_status()
            data = await r.json()
            await cache_set("weather", data); return data

async def get_weather_cached():
    return await cache_get("weather") or await fetch_weather()

def outfit_advice(temp: float, wind: float, rain: float, gender: str) -> str:
    base = []
    if temp < -10: base.append("очень холодно: тёплая куртка, шапка, перчатки")
    elif temp < 5: base.append("холодно: утепляйтесь, куртка и закрытая обувь")
    elif temp < 15: base.append("прохладно: лёгкая куртка/худи")
    elif temp < 25: base.append("комфортно: лёгкая одежда")
    else: base.append("жарко: лёгкая одежда и головной убор")
    if rain and rain > 0: base.append("зонт/дождевик")
    if wind and wind > 8: base.append("ветровка")
    base.append("подойдёт: кроссовки/удобная обувь")
    return "; ".join(base)
