import asyncio
import hashlib
import html
import logging
import re
import time

import httpx

logger = logging.getLogger(__name__)
GOOGLE_CHROME_URL = "https://clients5.google.com/translate_a/t"
GOOGLE_GTX_URL = "https://translate.googleapis.com/translate_a/single"
MYMEMORY_URL = "https://api.mymemory.translated.net/get"
GOOGLE_CHUNK = 3500
MYMEMORY_CHUNK = 450
CACHE_TTL_SECONDS = 60 * 60 * 12
SPANISH_MARKERS = ("ñ", "á", "é", "í", "ó", "ú", " que ", " de la ", " una ", " los ", " las ", " del ")
ENGLISH_MARKERS = (" the ", " and ", " of ", " with ", " is ", " from ", " his ", " her ")
TRANSLATE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

_cache: dict[str, tuple[float, str]] = {}
_inflight: dict[str, asyncio.Future] = {}


def looks_spanish(text: str) -> bool:
    lowered = f" {text.lower()} "
    spanish = sum(marker in lowered for marker in SPANISH_MARKERS)
    english = sum(marker in lowered for marker in ENGLISH_MARKERS)
    return spanish >= 2 and spanish > english


def _strip_markup(text: str) -> str:
    cleaned = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"</p>", "\n", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    cleaned = html.unescape(cleaned)
    return re.sub(r"\n{3,}", "\n\n", cleaned).strip()


def _chunks(text: str, size: int) -> list[str]:
    if len(text) <= size:
        return [text]

    parts: list[str] = []
    remaining = text
    while remaining:
        if len(remaining) <= size:
            parts.append(remaining)
            break
        window = remaining[:size]
        split_at = max(window.rfind(". "), window.rfind("\n"), window.rfind(" "))
        if split_at < size // 3:
            split_at = size
        parts.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].strip()
    return [part for part in parts if part]


def _clean(piece: str | None) -> str | None:
    if not piece:
        return None
    text = html.unescape(piece).strip()
    if not text or "MYMEMORY WARNING" in text.upper():
        return None
    return text


def _cache_key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _cache_get(text: str) -> str | None:
    entry = _cache.get(_cache_key(text))
    if not entry:
        return None
    expires_at, value = entry
    if expires_at < time.time():
        _cache.pop(_cache_key(text), None)
        return None
    return value


def _cache_set(text: str, value: str) -> None:
    _cache[_cache_key(text)] = (time.time() + CACHE_TTL_SECONDS, value)


def _google_text(payload) -> str | None:
    if isinstance(payload, str):
        return _clean(payload)
    if not isinstance(payload, list) or not payload:
        return None
    if isinstance(payload[0], str):
        return _clean("".join(item for item in payload if isinstance(item, str)))
    if isinstance(payload[0], list):
        return _clean("".join(row[0] for row in payload if row and row[0]))
    return None


async def _get_json(
    client: httpx.AsyncClient,
    url: str,
    params: dict,
    retries: int = 2,
) -> httpx.Response:
    delay = 0.8
    last_error: Exception | None = None
    for attempt in range(retries):
        response = await client.get(url, params=params, headers=TRANSLATE_HEADERS)
        if response.status_code != 429:
            response.raise_for_status()
            return response
        last_error = httpx.HTTPStatusError(
            "429 Too Many Requests",
            request=response.request,
            response=response,
        )
        if attempt == retries - 1:
            break
        await asyncio.sleep(delay)
        delay *= 2
    if last_error:
        raise last_error
    raise RuntimeError("No se pudo traducir")


async def _translate_google_chrome(client: httpx.AsyncClient, text: str) -> str | None:
    parts: list[str] = []
    for chunk in _chunks(text, GOOGLE_CHUNK):
        response = await _get_json(
            client,
            GOOGLE_CHROME_URL,
            {"client": "dict-chrome-ex", "sl": "auto", "tl": "es", "q": chunk},
        )
        cleaned = _google_text(response.json())
        if not cleaned:
            return None
        parts.append(cleaned)
    return " ".join(parts).strip() or None


async def _translate_google_gtx(client: httpx.AsyncClient, text: str) -> str | None:
    parts: list[str] = []
    for chunk in _chunks(text, GOOGLE_CHUNK):
        response = await _get_json(
            client,
            GOOGLE_GTX_URL,
            {"client": "gtx", "sl": "auto", "tl": "es", "dt": "t", "q": chunk},
            retries=1,
        )
        cleaned = _google_text(response.json())
        if not cleaned:
            return None
        parts.append(cleaned)
    return " ".join(parts).strip() or None


async def _translate_mymemory(client: httpx.AsyncClient, text: str) -> str | None:
    parts: list[str] = []
    for chunk in _chunks(text, MYMEMORY_CHUNK):
        response = await _get_json(
            client,
            MYMEMORY_URL,
            {"q": chunk, "langpair": "en|es"},
            retries=1,
        )
        payload = response.json()
        piece = _clean((payload.get("responseData") or {}).get("translatedText"))
        if not piece:
            return None
        parts.append(piece)
    return " ".join(parts).strip() or None


async def _translate_uncached(client: httpx.AsyncClient, source: str) -> str:
    for translator in (_translate_google_chrome, _translate_google_gtx, _translate_mymemory):
        try:
            translated = await translator(client, source)
            if translated and translated.lower() != source.lower():
                _cache_set(source, translated)
                return translated
        except Exception as exc:
            logger.warning("Traductor %s falló: %s", translator.__name__, exc)
    return source


async def translate_to_spanish(client: httpx.AsyncClient, text: str | None) -> str | None:
    if not text:
        return None

    source = _strip_markup(text)
    if not source:
        return None
    if looks_spanish(source):
        return source

    cached = _cache_get(source)
    if cached:
        return cached

    key = _cache_key(source)
    inflight = _inflight.get(key)
    if inflight:
        return await inflight

    loop = asyncio.get_running_loop()
    future: asyncio.Future = loop.create_future()
    _inflight[key] = future
    try:
        result = await _translate_uncached(client, source)
        future.set_result(result)
        return result
    except Exception as exc:
        future.set_exception(exc)
        raise
    finally:
        _inflight.pop(key, None)
