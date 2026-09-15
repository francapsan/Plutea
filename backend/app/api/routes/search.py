from typing import Annotated

from fastapi import APIRouter, Query

from app.schemas.search import SearchResponse
from app.services.catalog import search_catalog

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
async def search(
    q: Annotated[str, Query(min_length=1, max_length=200, description="Consulta en lenguaje natural")],
) -> SearchResponse:
    return await search_catalog(q.strip())
