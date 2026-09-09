# PLUTEA - Your entertainment shelf.

PLUTEA es una plataforma web para gestionar colecciones de entretenimiento digital (libros, videojuegos, cine y más) mediante **estanterías visuales**. En lugar de listas de texto, las portadas ocupan el centro de la interfaz: cada usuario dispone de un espacio propio —*Mi Habitación*— donde coleccionar, organizar y consultar sus obras.

El producto se concibe como un agregador visual unificado, frente a herramientas fragmentadas por medio (literatura, cine, videojuegos).

## Stack tecnológico (Fase 2)

- **React** — componentes UI modulares
- **CSS moderno** — Flexbox y Grid (sin librerías de UI)
- **Vite** — entorno de desarrollo y empaquetado

Esta fase no incluye APIs ni catálogo: la navegación y las fichas son solo estructura visual con placeholders.

## Estado

**Fase 2 — Navegación de Mi Habitación y superficies de interacción**

Objetivo: recorrer el layout como si fuera la habitación del usuario. El menú cambia de vista, la barra de búsqueda ocupa su lugar y cada hueco abre una ficha vacía.

## Estructura

```
src/
├── components/layout/   Sidebar, TopBar y contenedor principal
├── features/shelves/     Huecos, cuadrícula y ficha placeholder
└── pages/                Vista Dashboard (habitación y estantería)
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
