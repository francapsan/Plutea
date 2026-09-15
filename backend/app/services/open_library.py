import httpx

from app.schemas.search import SearchItem

OPEN_LIBRARY_SEARCH_URL = "https://openlibrary.org/search.json"
OPEN_LIBRARY_WORK_URL = "https://openlibrary.org/works/{work_id}.json"
COVER_URL = "https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
ISBN_COVER_URL = "https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg?default=false"


def _text_value(value) -> str | None:
    if not value:
        return None
    if isinstance(value, dict):
        text = value.get("value")
        return str(text).strip() if text else None
    text = str(value).strip()
    return text or None


def first_isbn(values) -> str | None:
    if not values:
        return None
    if isinstance(values, str):
        values = [values]

    candidates: list[str] = []
    for value in values:
        digits = "".join(ch for ch in str(value) if ch.isdigit() or ch.upper() == "X")
        if len(digits) in (10, 13):
            candidates.append(digits)

    candidates.sort(key=lambda isbn: 0 if len(isbn) == 13 else 1)
    return candidates[0] if candidates else None


def cover_url_from_isbns(values) -> str | None:
    isbn = first_isbn(values)
    if not isbn:
        return None
    return ISBN_COVER_URL.format(isbn=isbn)


async def search_open_library(
    client: httpx.AsyncClient,
    query: str,
    limit: int = 15,
) -> list[SearchItem]:
    response = await client.get(
        OPEN_LIBRARY_SEARCH_URL,
        params={
            "q": query,
            "limit": limit,
            "fields": "key,title,author_name,first_publish_year,cover_i,first_sentence",
        },
    )
    response.raise_for_status()
    payload = response.json()

    items: list[SearchItem] = []
    for doc in payload.get("docs", []):
        work_key = doc.get("key")
        title = doc.get("title")
        if not work_key or not title:
            continue

        work_id = work_key.rsplit("/", 1)[-1]
        authors = doc.get("author_name") or []
        year = doc.get("first_publish_year")
        cover_id = doc.get("cover_i")
        first_sentence = _text_value(
            (doc.get("first_sentence") or [None])[0]
            if isinstance(doc.get("first_sentence"), list)
            else doc.get("first_sentence")
        )

        items.append(
            SearchItem(
                id=f"open_library:{work_id}",
                source="open_library",
                media_type="book",
                title=title,
                subtitle=", ".join(authors[:3]) or None,
                image_url=COVER_URL.format(cover_id=cover_id) if cover_id else None,
                year=str(year) if year else None,
                external_id=work_id,
                description=first_sentence,
            )
        )

    return items


async def fetch_work(client: httpx.AsyncClient, work_id: str) -> dict:
    response = await client.get(OPEN_LIBRARY_WORK_URL.format(work_id=work_id))
    response.raise_for_status()
    return response.json()


def work_description(work: dict) -> str | None:
    description = _text_value(work.get("description"))
    if description:
        return description

    excerpts = work.get("excerpts") or []
    if excerpts and isinstance(excerpts[0], dict):
        return _text_value(excerpts[0].get("excerpt") or excerpts[0].get("comment"))
    return None


async def description_from_open_library(
    client: httpx.AsyncClient,
    *,
    title: str | None = None,
    isbns: list[str] | None = None,
) -> str | None:
    isbn = first_isbn(isbns)
    query = isbn or title
    if not query:
        return None

    items = await search_open_library(client, query, limit=1)
    if not items:
        return None

    try:
        work = await fetch_work(client, items[0].external_id)
        return work_description(work) or items[0].description
    except httpx.HTTPError:
        return items[0].description


async def cover_from_open_library(client: httpx.AsyncClient, title: str | None) -> str | None:
    if not title:
        return None
    items = await search_open_library(client, title, limit=1)
    if not items:
        return None
    return items[0].image_url
