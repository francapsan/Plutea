from typing import Annotated

from fastapi import APIRouter, Path, Query

from app.schemas.search import BookDetail
from app.services.catalog import BOOK_ID_PATTERN, get_book_detail

router = APIRouter()


@router.get("/books/{book_id}", response_model=BookDetail)
async def book_detail(
    book_id: Annotated[
        str,
        Path(pattern=BOOK_ID_PATTERN, description="Identificador hardcover:123 u OL…W"),
    ],
    fallback: Annotated[str | None, Query(max_length=2000)] = None,
) -> BookDetail:
    return await get_book_detail(book_id, fallback=fallback)
