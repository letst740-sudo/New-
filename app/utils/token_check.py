import re
TOKEN_RE = re.compile(r"^\d{4,}:[A-Za-z0-9_-]{35,}$")
def mask_token(token: str) -> str:
    if not token: return "EMPTY"
    return token[:6] + "..." + token[-4:] + f" (len={len(token)})"
def is_probably_valid(token: str | None) -> bool:
    return bool(token) and TOKEN_RE.fullmatch(token) is not None
