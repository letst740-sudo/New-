from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
import os

def _load_env_multi():
    for p in [Path.cwd()/".env", Path(__file__).resolve().parent.parent/".env", Path(__file__).resolve().parent.parent.parent/".env"]:
        if p.exists():
            load_dotenv(p, override=True)
            return str(p)
    load_dotenv(); return None
ENV_PATH = _load_env_multi()

class Settings(BaseModel):
    bot_token: str = os.getenv("BOT_TOKEN","")
    admin_ids: list[int] = [int(x) for x in os.getenv("ADMIN_IDS","").replace(" ","").split(",") if x]
    weather_lat: float = float(os.getenv("WEATHER_LAT","51.713"))
    weather_lon: float = float(os.getenv("WEATHER_LON","46.741"))
    tz: str = os.getenv("TZ","Europe/Saratov")
    afisha_url: str = os.getenv("AFISHA_URL","")
    llm_api_base: str = os.getenv("LLM_API_BASE","")
    llm_api_key: str = os.getenv("LLM_API_KEY","")
    llm_model: str = os.getenv("LLM_MODEL","")
    fallback_api_base: str = os.getenv("FALLBACK_API_BASE","http://localai:8080/v1")
    fallback_api_key: str = os.getenv("FALLBACK_API_KEY","")
    fallback_model: str = os.getenv("FALLBACK_MODEL","qwen2.5-7b-instruct-q4_0")
    max_tokens: int = int(os.getenv("MAX_TOKENS","300"))
    max_tokens_fallback: int = int(os.getenv("MAX_TOKENS_FALLBACK","256"))
    temperature: float = float(os.getenv("TEMPERATURE","0.3"))
    vk_url: str = os.getenv("VK_URL","https://vk.com/marks_city")
    tg_url: str = os.getenv("TG_URL","https://t.me/TheMarksCity")
    contact_url: str = os.getenv("CONTACT_URL","https://t.me/Listen_mp4")
settings = Settings()
