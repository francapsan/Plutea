import asyncio
import logging

import httpx

from app.core.config import settings
from app.schemas.search import SearchItem
from app.services.open_library import (
    cover_from_open_library,
    cover_url_from_isbns,
    first_isbn,
)

logger = logging.getLogger(__name__)

GRAPHQL_URL = "https://api.hardcover.app/v1/graphql"
SEARCH_LIMIT = 15

SEARCH_QUERY = """
query SearchBooks($query: String!, $perPage: Int!) {
  search(query: $query, query_type: "Book", per_page: $perPage, page: 1) {
    results
  }
}
"""

_BOOK_SELECTION = """
    id
    title
    subtitle
    description
    release_year
    cached_image
    image {
      url
    }
    contributions {
      author {
        name
      }
    }
    default_cover_edition {
      isbn_10
      isbn_13
      image {
        url
      }
    }
    default_physical_edition {
      isbn_10
      isbn_13
      image {
        url
      }
    }
    default_ebook_edition {
      isbn_10
      isbn_13
      image {
        url
      }
    }
    images(limit: 8) {
      url
    }
"""

BOOKS_QUERY = """
query GetBooks($ids: [Int!]!) {
  books(where: {id: {_in: $ids}}) {
""" + _BOOK_SELECTION + """
  }
}
"""

BOOK_QUERY = """
query GetBook($id: Int!) {
  books(where: {id: {_eq: $id}}) {
""" + _BOOK_SELECTION + """
  }
}
"""


class HardcoverError(Exception):
    pass


def is_configured() -> bool:
    return bool(settings.hardcover_api_token.strip())


def _auth_header() -> str:
    token = settings.hardcover_api_token.strip()
    if not token:
        raise HardcoverError("Falta HARDCOVER_API_TOKEN")
    if token.lower().startswith("bearer "):
        return token
    return f"Bearer {token}"


def _text(value) -> str | None:
    if not value:
        return None
    if isinstance(value, dict):
        text = value.get("value") or value.get("url")
        return str(text).strip() if text else None
    text = str(value).strip()
    return text or None


def _image_url(payload: dict | None) -> str | None:
    if not payload:
        return None

    image = payload.get("image")
    if isinstance(image, str) and image.startswith("http"):
        return image
    if isinstance(image, dict):
        url = _text(image.get("url") or image.get("image"))
        if url and url.startswith("http"):
            return url

    cached = payload.get("cached_image")
    if isinstance(cached, str) and cached.startswith("http"):
        return cached
    if isinstance(cached, dict):
        url = _text(cached.get("url") or cached.get("image"))
        if url and url.startswith("http"):
            return url

    return None


def _author_names(payload: dict) -> str | None:
    names = payload.get("author_names") or []
    if isinstance(names, str):
        names = [names]
    collected = [str(name).strip() for name in names if name]

    if not collected:
        for contribution in payload.get("contributions") or []:
            author = (contribution or {}).get("author") or {}
            name = _text(author.get("name"))
            if name:
                collected.append(name)

    return ", ".join(collected[:3]) or None


def _year(payload: dict) -> str | None:
    year = payload.get("release_year")
    return str(year) if year else None


def _isbns(payload: dict) -> list[str]:
    values: list[str] = []
    raw = payload.get("isbns") or []
    if isinstance(raw, str):
        raw = [raw]
    values.extend(str(item) for item in raw if item)

    for key in ("default_cover_edition", "default_physical_edition", "default_ebook_edition"):
        edition = payload.get(key) or {}
        for field in ("isbn_13", "isbn_10"):
            if edition.get(field):
                values.append(str(edition[field]))

    unique: list[str] = []
    seen: set[str] = set()
    for value in values:
        isbn = first_isbn([value])
        if isbn and isbn not in seen:
            seen.add(isbn)
            unique.append(isbn)
    return unique


def _cover_score(url: str) -> int:
    lowered = url.lower()
    score = 0
    if "assets.hardcover.app" in lowered:
        score += 20
    if any(marker in lowered for marker in ("_sx98_", "_sx50_", "_sx75_")):
        score -= 40
    if "-l.jpg" in lowered or "-l.jpeg" in lowered:
        score += 8
    return score


def _image_candidates(payload: dict) -> list[str]:
    urls: list[str] = []
    sources = [
        payload,
        payload.get("default_cover_edition") or {},
        payload.get("default_physical_edition") or {},
        payload.get("default_ebook_edition") or {},
    ]
    for source in sources:
        url = _image_url(source)
        if url:
            urls.append(url)

    for image in payload.get("images") or []:
        if isinstance(image, dict):
            url = _text(image.get("url"))
        elif isinstance(image, str):
            url = _text(image)
        else:
            url = None
        if url and url.startswith("http"):
            urls.append(url)

    isbn_cover = cover_url_from_isbns(_isbns(payload))
    if isbn_cover:
        urls.append(isbn_cover)

    unique: list[str] = []
    seen: set[str] = set()
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique.append(url)
    return unique


def _cover_url(payload: dict) -> str | None:
    candidates = _image_candidates(payload)
    if not candidates:
        return None
    return max(candidates, key=_cover_score)


def _iter_search_documents(results) -> list[dict]:
    if not results:
        return []
    if isinstance(results, list):
        rows = results
    elif isinstance(results, dict):
        rows = results.get("hits") or results.get("docs") or results.get("results") or []
    else:
        return []

    documents: list[dict] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        document = row.get("document") if isinstance(row.get("document"), dict) else row
        if document.get("id") and document.get("title"):
            documents.append(document)
    return documents


def _to_item(payload: dict) -> SearchItem | None:
    book_id = payload.get("id")
    title = _text(payload.get("title"))
    try:
        external_id = str(int(book_id))
    except (TypeError, ValueError):
        return None
    if not title:
        return None

    return SearchItem(
        id=f"hardcover:{external_id}",
        source="hardcover",
        media_type="book",
        title=title,
        subtitle=_author_names(payload) or _text(payload.get("subtitle")),
        image_url=_cover_url(payload),
        year=_year(payload),
        external_id=external_id,
        description=_text(payload.get("description")),
    )


def _merge(hit: dict, book: dict | None) -> dict:
    if not book:
        return hit
    merged = {**hit, **{key: value for key, value in book.items() if value not in (None, "", [], {})}}
    if not _image_url(merged):
        merged["image"] = hit.get("image") or book.get("image")
    if not merged.get("isbns"):
        merged["isbns"] = _isbns(hit) or _isbns(book)
    if not merged.get("author_names") and not merged.get("contributions"):
        merged["contributions"] = book.get("contributions") or hit.get("contributions")
    return merged


async def graphql(
    client: httpx.AsyncClient,
    query: str,
    variables: dict | None = None,
) -> dict:
    response = await client.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables or {}},
        headers={
            "Authorization": _auth_header(),
            "Content-Type": "application/json",
        },
    )
    response.raise_for_status()
    payload = response.json()
    errors = payload.get("errors") or []
    if errors:
        message = errors[0].get("message") if isinstance(errors[0], dict) else str(errors[0])
        raise HardcoverError(message or "Error GraphQL de Hardcover")
    return payload.get("data") or {}


async def fetch_books(client: httpx.AsyncClient, ids: list[int]) -> dict[int, dict]:
    if not ids:
        return {}
    data = await graphql(client, BOOKS_QUERY, {"ids": ids})
    books: dict[int, dict] = {}
    for book in data.get("books") or []:
        try:
            books[int(book["id"])] = book
        except (KeyError, TypeError, ValueError):
            continue
    return books


async def fetch_book(client: httpx.AsyncClient, book_id: int) -> dict:
    data = await graphql(client, BOOK_QUERY, {"id": book_id})
    books = data.get("books") or []
    if not books:
        raise HardcoverError("Libro no encontrado")
    return books[0]


async def search_hardcover(client: httpx.AsyncClient, query: str, limit: int = SEARCH_LIMIT) -> list[SearchItem]:
    data = await graphql(client, SEARCH_QUERY, {"query": query, "perPage": limit})
    hits = _iter_search_documents((data.get("search") or {}).get("results"))
    ids: list[int] = []
    for hit in hits:
        try:
            ids.append(int(hit["id"]))
        except (TypeError, ValueError):
            continue

    try:
        books = await fetch_books(client, ids)
    except Exception as exc:
        logger.warning("No se pudieron hidratar fichas de Hardcover: %s", exc)
        books = {}

    items: list[SearchItem] = []
    for hit in hits:
        try:
            book_id = int(hit["id"])
        except (TypeError, ValueError):
            continue
        item = _to_item(_merge(hit, books.get(book_id)))
        if item:
            items.append(item)

    await _fill_missing_covers(client, items)
    return items


async def _fill_missing_covers(client: httpx.AsyncClient, items: list[SearchItem]) -> None:
    missing = [item for item in items if not item.image_url]
    if not missing:
        return

    async def fill(item: SearchItem) -> None:
        try:
            cover = await cover_from_open_library(client, item.title)
        except Exception as exc:
            logger.warning("Open Library no pudo completar la portada de %s: %s", item.title, exc)
            return
        if cover:
            item.image_url = cover

    await asyncio.gather(*(fill(item) for item in missing))


def book_isbns(book: dict) -> list[str]:
    return _isbns(book)


def book_image_url(book: dict) -> str | None:
    return _cover_url(book)


def book_authors(book: dict) -> str | None:
    return _author_names(book)
