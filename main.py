import asyncio, logging, sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.config import settings, ENV_PATH
from app.handlers.common import router as common_router
from app.scheduler import scheduler, setup_jobs
from app.storage import init_db
from app.middleware import BanGuard, RegGuard
from app.utils.token_check import is_probably_valid, mask_token

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("markscity")

def _fail(msg: str):
    log.error(msg); print("\n" + msg + "\n", file=sys.stderr)

async def main():
    token = (settings.bot_token or "").strip()
    if not is_probably_valid(token):
        _fail(f"❌ BOT_TOKEN не найден или не проходит валидацию. Сейчас вижу: {mask_token(token)}\n"
              f"Где искал .env: {ENV_PATH or '(стандартный поиск)'}\n"
              f"Проверьте файл .env в корне проекта: BOT_TOKEN=123456789:ABC...")
        return
    await init_db()
    bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.message.middleware(BanGuard()); dp.callback_query.middleware(BanGuard())
    dp.message.middleware(RegGuard()); dp.callback_query.middleware(RegGuard())
    dp.include_router(common_router)
    setup_jobs(); scheduler.start()
    log.info("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
