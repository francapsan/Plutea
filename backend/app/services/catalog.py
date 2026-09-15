import logging

from fastapi import HTTPException
import httpx

from app.schemas.search import BookDetail, SearchResponse
from app.services.hardcover import (
    HardcoverError,
    book_authors,
    book_image_url,
    book_isbns,
    fetch_book,
    is_configured,
    search_hardcover,
)
from app.services.open_library import (
    COVER_URL,
    cover_from_open_library,
    cover_url_from_isbns,
    description_from_open_library,
    fetch_work,
    search_open_library,
    work_description,
)
from app.services.translate import translate_to_spanish

logger = logging.getLogger(__name__)
HTTP_HEADERS = {
    "User-Agent": "PLUTEA/0.1 (https://github.com/francapsan/Plutea)",
    "Accept": "application/json",
}
BOOK_ID_PATTERN = r"^(hardcover:\d+|open_library:OL\d+W|OL\d+W)$"


def parse_book_id(book_id: str) -> tuple[str, str]:
    if book_id.startswith("hardcover:"):
        return "hardcover", book_id.split(":", 1)[1]
    if book_id.startswith("open_library:"):
        return "open_library", book_id.split(":", 1)[1]
    return "open_library", book_id


async def search_catalog(query: str) -> SearchResponse:
    timeout = httpx.Timeout(15.0)
    sources: dict[str, str] = {}

    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        headers=HTTP_HEADERS,
    ) as client:
        if is_configured():
            try:
                results = await search_hardcover(client, query)
                sources["hardcover"] = "ok"
                if results:
                    sources["open_library"] = "skipped"
                    return SearchResponse(query=query, results=results, sources=sources)
            except Exception as exc:
                logger.warning("Hardcover falló: %s", exc)
                sources["hardcover"] = "error"
        else:
            sources["hardcover"] = "skipped"

        try:
            results = await search_open_library(client, query)
            sources["open_library"] = "ok"
            return SearchResponse(query=query, results=results, sources=sources)
        except Exception as exc:
            logger.warning("Open Library falló: %s", exc)
            sources["open_library"] = "error"
            return SearchResponse(query=query, results=[], sources=sources)


async def get_book_detail(book_id: str, fallback: str | None = None) -> BookDetail:
    source, external_id = parse_book_id(book_id)
    timeout = httpx.Timeout(40.0)

    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        headers=HTTP_HEADERS,
    ) as client:
        if source == "hardcover":
            return await _hardcover_detail(client, external_id, fallback)
        return await _open_library_detail(client, external_id, fallback)


async def _hardcover_detail(
    client: httpx.AsyncClient,
    external_id: str,
    fallback: str | None,
) -> BookDetail:
    if not is_configured():
        raise HTTPException(status_code=503, detail="Hardcover no está configurado")

    try:
        book = await fetch_book(client, int(external_id))
    except HardcoverError as exc:
        raise HTTPException(status_code=404, detail="Libro no encontrado") from exc
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code in {401, 403}:
            raise HTTPException(status_code=502, detail="Token de Hardcover no válido") from exc
        raise HTTPException(status_code=502, detail="Hardcover no está disponible") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Hardcover no está disponible") from exc

    isbns = book_isbns(book)
    image_url = book_image_url(book) or cover_url_from_isbns(isbns)
    raw_description = _text(book.get("description")) or fallback

    if not raw_description or not image_url:
        try:
            ol_description = await description_from_open_library(
                client,
                title=book.get("title"),
                isbns=isbns,
            )
        except Exception as exc:
            logger.warning("Open Library no pudo completar la ficha: %s", exc)
            ol_description = None
        raw_description = raw_description or ol_description
        if not image_url:
            image_url = cover_url_from_isbns(isbns) or await cover_from_open_library(
                client,
                book.get("title"),
            )

    description = await translate_to_spanish(client, raw_description)

    return BookDetail(
        id=f"hardcover:{external_id}",
        source="hardcover",
        media_type="book",
        title=book.get("title") or "Sin título",
        subtitle=book_authors(book) or _text(book.get("subtitle")),
        image_url=image_url,
        year=str(book["release_year"]) if book.get("release_year") else None,
        external_id=external_id,
        description=description,
    )


async def _open_library_detail(
    client: httpx.AsyncClient,
    work_id: str,
    fallback: str | None,
) -> BookDetail:
    try:
        work = await fetch_work(client, work_id)
        raw_description = work_description(work) or fallback
        description = await translate_to_spanish(client, raw_description)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Libro no encontrado") from exc
        raise HTTPException(status_code=502, detail="Open Library no está disponible") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Open Library no está disponible") from exc

    covers = work.get("covers") or []
    cover_id = covers[0] if covers else None
    key = work.get("key") or f"/works/{work_id}"
    external_id = key.rsplit("/", 1)[-1]

    return BookDetail(
        id=f"open_library:{external_id}",
        source="open_library",
        media_type="book",
        title=work.get("title") or "Sin título",
        subtitle=None,
        image_url=COVER_URL.format(cover_id=cover_id) if cover_id else None,
        year=None,
        external_id=external_id,
        description=description,
    )


def _text(value) -> str | None:
    if not value:
        return None
    text = str(value).strip()
    return text or None
