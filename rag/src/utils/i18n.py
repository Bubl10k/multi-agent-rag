import json
from enum import StrEnum
from functools import lru_cache
from pathlib import Path

_LOCALES_DIR = Path(__file__).parent.parent / "locales"


class Locale(StrEnum):
    EN = "en"
    UK = "uk"


DEFAULT_LOCALE = Locale.EN

LANGUAGE_NAMES: dict[Locale, str] = {
    Locale.EN: "English",
    Locale.UK: "Ukrainian",
}


@lru_cache
def _catalog(locale: Locale) -> dict[str, str]:
    path = _LOCALES_DIR / f"{locale.value}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_locale(accept_language: str | None) -> Locale:
    """Pick the best-matching Locale from an Accept-Language header value."""
    if not accept_language:
        return DEFAULT_LOCALE

    for part in accept_language.split(","):
        code = part.split(";")[0].strip().split("-")[0].lower()
        try:
            return Locale(code)
        except ValueError:
            continue
    return DEFAULT_LOCALE


def translate(key: str, locale: Locale = DEFAULT_LOCALE, **params: str) -> str:
    """Translate an error/message code to the given locale, falling back to English, then the key itself."""
    message = _catalog(locale).get(key) or _catalog(DEFAULT_LOCALE).get(key) or key
    return message.format(**params) if params else message
