from aiohttp import ClientSession
from app.storage import cache_get, cache_set

async def fetch_fiat():
    url = "https://api.exchangerate.host/latest?base=RUB&symbols=USD,EUR"
    async with ClientSession() as s:
        async with s.get(url, timeout=10) as r:
            r.raise_for_status(); data = await r.json()
            await cache_set("fiat_rates", data); return data

async def fetch_crypto():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,toncoin,ethereum&vs_currencies=usd"
    async with ClientSession() as s:
        async with s.get(url, timeout=10) as r:
            r.raise_for_status(); data = await r.json()
            await cache_set("crypto_rates", data); return data

async def get_rates_cached():
    return (await cache_get("fiat_rates") or await fetch_fiat()), (await cache_get("crypto_rates") or await fetch_crypto())
