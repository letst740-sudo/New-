from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from app.storage import get_user

class BanGuard(BaseMiddleware):
    async def __call__(self, handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]], event, data: Dict[str, Any]) -> Any:
        return await handler(event, data)


class RegGuard(BaseMiddleware):
    async def __call__(self, handler, event, data):
        from_user = getattr(event, "from_user", None)
        if from_user is None:
            return await handler(event, data)

        from app.config import settings
        if from_user.id in settings.admin_ids:
            return await handler(event, data)

        # allow FSM registration states
        state = data.get("state")
        if state:
            cur = await state.get_state()
            from app.states import RegStates
            if cur in {RegStates.ASK_GENDER.state, RegStates.ASK_AGE.state}:
                return await handler(event, data)

        from app.storage import get_user
        user = await get_user(from_user.id)
        txt = getattr(event, "text", "") or ""
        data_text = getattr(event, "data", "") or ""

        allow = bool(user) or txt.startswith("/start") or data_text.startswith("gender:") or data_text in {"reg:start","menu:back"}
        if not allow:
            try:
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📝 Зарегистрироваться", callback_data="reg:start")]])
                await event.bot.send_message(from_user.id, "Пожалуйста, пройдите быструю регистрацию, чтобы пользоваться функциями.", reply_markup=kb)
            except Exception:
                pass
            return
        return await handler(event, data)
