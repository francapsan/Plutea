# PLUTEA - Your entertainment shelf.

PLUTEA es una plataforma web para gestionar colecciones de entretenimiento digital (libros, videojuegos, cine y más) mediante **estanterías visuales**. En lugar de listas de texto, las portadas ocupan el centro de la interfaz: cada usuario dispone de un espacio propio —*Mi Habitación*— donde coleccionar, organizar y consultar sus obras.

## Stack

- **Frontend:** React + CSS (Flexbox/Grid) + Vite
- **Backend:** Python FastAPI (agregador BFF)
- **Catálogo:** Hardcover (principal) + Open Library (apoyo para portadas/sinopsis)

## Estado

**Fase 4 — Backend de búsqueda**

El frontend de habitación y estanterías sigue siendo visual. La búsqueda consulta `GET /api/search`: **Hardcover** si hay token, y **Open Library** si falta el token, Hardcover falla o no hay resultados. Videojuegos, cine y PostgreSQL quedan para más adelante.

## Estructura

```
src/                 Frontend React
backend/
├── app/
│   ├── main.py              FastAPI, CORS y /health
│   ├── api/routes/search.py GET /api/search
│   ├── services/            Hardcover y Open Library
│   └── schemas/search.py    Contrato unificado
└── .env.example
```

## Frontend

```bash
npm install
npm run dev
```

Vite queda en `http://localhost:5173` y reenvía `/api` al backend (`http://127.0.0.1:8000`).

## Backend

Requisitos: Python 3.12 o superior.

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

En macOS/Linux: `source .venv/bin/activate` y `cp .env.example .env`.

Documentación interactiva: `http://127.0.0.1:8000/docs`.

Copia `backend/.env.example` a `backend/.env`. Crea un token en Hardcover (cuenta → Hardcover API) y pégalo en `HARDCOVER_API_TOKEN`. El archivo `.env` queda fuera de Git: no lo subas a GitHub. Sin token, la búsqueda usa solo Open Library.

```bash
curl "http://127.0.0.1:8000/api/search?q=dune"
```
