from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.books import router as books_router
from app.api.routes.search import router as search_router
from app.core.config import settings

app = FastAPI(
    title="PLUTEA API",
    description="Agregador BFF de metadatos de entretenimiento para las estanterías de PLUTEA.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router, prefix="/api")
app.include_router(books_router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
