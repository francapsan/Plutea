from typing import Literal

from pydantic import BaseModel

MediaType = Literal["book"]
SourceName = Literal["hardcover", "open_library"]
SourceStatus = Literal["ok", "error", "skipped"]


class SearchItem(BaseModel):
    id: str
    source: SourceName
    media_type: MediaType
    title: str
    subtitle: str | None = None
    image_url: str | None = None
    year: str | None = None
    external_id: str
    description: str | None = None


class SearchResponse(BaseModel):
    query: str
    results: list[SearchItem]
    sources: dict[SourceName, SourceStatus]


class BookDetail(SearchItem):
    pass
