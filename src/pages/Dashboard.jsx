import { useEffect, useState } from 'react'
import { MainLayout } from '../components/layout/MainLayout'
import { searchCatalog } from '../features/search/api'
import { ItemDetail } from '../features/shelves/ItemDetail'
import { ShelfGrid } from '../features/shelves/ShelfGrid'
import {
  PLACEHOLDER_SHELVES,
  ROOM_VIEW,
  SEARCH_VIEW,
} from '../features/shelves/placeholders'
import './Dashboard.css'

export function Dashboard({
  view,
  searchQuery,
  collection,
  onNavigate,
  onSearch,
  selectedItem,
  onSelectItem,
  onAddToShelf,
}) {
  const activeShelf = PLACEHOLDER_SHELVES.find((shelf) => shelf.id === view)
  const selectedIndex =
    selectedItem && selectedItem.view === view ? selectedItem.index : null
  const shelfBooks = activeShelf ? collection[activeShelf.id] ?? [] : []

  return (
    <MainLayout
      view={view}
      onNavigate={onNavigate}
      onSearch={onSearch}
      detail={
        selectedItem ? (
          <ItemDetail
            item={selectedItem.item}
            collection={collection}
            onAddToShelf={onAddToShelf}
            onClose={() => onSelectItem(null)}
          />
        ) : null
      }
    >
      {view === ROOM_VIEW ? (
        <RoomView
          collection={collection}
          selectedItem={selectedItem}
          onNavigate={onNavigate}
          onSelectItem={onSelectItem}
        />
      ) : view === SEARCH_VIEW ? (
        <SearchView
          query={searchQuery}
          selectedIndex={selectedIndex}
          onNavigate={onNavigate}
          onSelectItem={onSelectItem}
        />
      ) : (
        <section>
          <header className="dashboard__header">
            <h2 className="dashboard__title">{activeShelf?.name ?? 'Estantería'}</h2>
            <p className="dashboard__subtitle">
              {shelfBooks.length
                ? `${shelfBooks.length} libro${shelfBooks.length === 1 ? '' : 's'} en esta estantería`
                : 'Huecos vacíos — añade un libro desde la búsqueda'}
            </p>
          </header>
          <ShelfGrid
            items={shelfBooks.length ? shelfBooks : undefined}
            selectedIndex={selectedIndex}
            onSelectItem={(index) =>
              onSelectItem({
                view,
                index,
                item: shelfBooks[index],
              })
            }
          />
        </section>
      )}
    </MainLayout>
  )
}

function RoomView({ collection, selectedItem, onNavigate, onSelectItem }) {
  return (
    <section>
      <header className="dashboard__header">
        <h2 className="dashboard__title">Mi Habitación</h2>
        <p className="dashboard__subtitle">
          Tres estanterías de ejemplo para recorrer el espacio
        </p>
      </header>

      <div className="room">
        {PLACEHOLDER_SHELVES.map((shelf) => {
          const books = collection[shelf.id] ?? []
          return (
            <section key={shelf.id} className="room__shelf">
              <header className="room__shelf-header">
                <h3>{shelf.name}</h3>
                <button type="button" onClick={() => onNavigate(shelf.id)}>
                  Ver estantería
                </button>
              </header>
              <ShelfGrid
                compact
                items={books.length ? books : undefined}
                slots={6}
                selectedIndex={
                  selectedItem?.view === shelf.id ? selectedItem.index : null
                }
                onSelectItem={(index) =>
                  onSelectItem({
                    view: shelf.id,
                    index,
                    item: books[index],
                  })
                }
              />
            </section>
          )
        })}
      </div>
    </section>
  )
}

function SearchView({ query, selectedIndex, onNavigate, onSelectItem }) {
  const [results, setResults] = useState(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    let cancelled = false
    setResults(null)
    setError(false)

    searchCatalog(query)
      .then((payload) => {
        if (!cancelled) {
          setResults(payload.results ?? [])
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError(true)
          setResults([])
        }
      })

    return () => {
      cancelled = true
    }
  }, [query])

  const subtitle = error
    ? `Búsqueda: «${query}» — no se pudo consultar el catálogo`
    : results
      ? `Búsqueda: «${query}» — ${results.length} resultado${results.length === 1 ? '' : 's'}`
      : `Búsqueda: «${query}» — consultando catálogo…`

  return (
    <section>
      <header className="dashboard__header">
        <h2 className="dashboard__title">Resultados</h2>
        <p className="dashboard__subtitle">{subtitle}</p>
        <button
          type="button"
          className="dashboard__back"
          onClick={() => onNavigate(ROOM_VIEW)}
        >
          Volver a Mi Habitación
        </button>
      </header>
      {results && results.length === 0 ? (
        <p className="dashboard__empty">No hay portadas para esta consulta todavía.</p>
      ) : (
        <ShelfGrid
          items={results ?? undefined}
          selectedIndex={selectedIndex}
          onSelectItem={(index) =>
            onSelectItem({
              view: SEARCH_VIEW,
              index,
              item: results?.[index],
            })
          }
        />
      )}
    </section>
  )
}
