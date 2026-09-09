# PLUTEA - Your entertainment shelf.

PLUTEA es una plataforma web para gestionar colecciones de entretenimiento digital (libros, videojuegos, cine y más) mediante **estanterías visuales**. En lugar de listas de texto, las portadas ocupan el centro de la interfaz: cada usuario dispone de un espacio propio —*Mi Habitación*— donde coleccionar, organizar y consultar sus obras.

El producto se concibe como un agregador visual unificado, frente a herramientas fragmentadas por medio (literatura, cine, videojuegos).

## Stack tecnológico (Fase 1)

- **React** — componentes UI modulares
- **CSS moderno** — Flexbox y Grid (sin librerías de UI)
- **Vite** — entorno de desarrollo y empaquetado

Esta fase no incluye APIs, estado de datos ni contenido simulado: solo estructura visual con placeholders.

## Estado

**Fase 1 — Esqueleto Visual y Maquetación**

Objetivo: definir el wireframe en código (sidebar fijo, área de contenido y cuadrícula de huecos vacíos en la estantería) para validar el layout y el comportamiento responsive.

## Estructura

```
src/
├── components/layout/   Sidebar y contenedor principal
├── features/shelves/     Huecos (ItemCard) y cuadrícula (ShelfGrid)
└── pages/                Vista Dashboard
```

## Instalación

Requisitos: [Node.js](https://nodejs.org/) 18 o superior.

```bash
npm install
npm run dev
```

La aplicación quedará disponible en `http://localhost:5173`.

Otros comandos:

```bash
npm run build    # Compilación de producción
npm run preview  # Vista previa del build
```
