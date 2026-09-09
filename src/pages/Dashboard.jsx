import { MainLayout } from '../components/layout/MainLayout'
import { ItemDetail } from '../features/shelves/ItemDetail'
import { ShelfGrid } from '../features/shelves/ShelfGrid'
import {
  PLACEHOLDER_SHELVES,
  ROOM_VIEW,
} from '../features/shelves/placeholders'
import './Dashboard.css'

export function Dashboard({ view, onNavigate, selectedItem, onSelectItem }) {
  const activeShelf = PLACEHOLDER_SHELVES.find((shelf) => shelf.id === view)
  const selectedIndex =
    selectedItem && selectedItem.view === view ? selectedItem.index : null

  return (
    <MainLayout
      view={view}
      onNavigate={onNavigate}
      detail={selectedItem ? <ItemDetail onClose={() => onSelectItem(null)} /> : null}
    >
      {view === ROOM_VIEW ? (
        <RoomView
          selectedItem={selectedItem}
          onNavigate={onNavigate}
          onSelectItem={onSelectItem}
        />
      ) : (
        <section>
          <header className="dashboard__header">
            <h2 className="dashboard__title">{activeShelf?.name ?? 'Estantería'}</h2>
            <p className="dashboard__subtitle">Huecos vacíos — esqueleto visual</p>
          </header>
          <ShelfGrid
            selectedIndex={selectedIndex}
            onSelectItem={(index) => onSelectItem({ view, index })}
          />
        </section>
      )}
    </MainLayout>
  )
}

function RoomView({ selectedItem, onNavigate, onSelectItem }) {
  return (
    <section>
      <header className="dashboard__header">
        <h2 className="dashboard__title">Mi Habitación</h2>
        <p className="dashboard__subtitle">
          Tres estanterías de ejemplo para recorrer el espacio
        </p>
      </header>

      <div className="room">
        {PLACEHOLDER_SHELVES.map((shelf) => (
          <section key={shelf.id} className="room__shelf">
            <header className="room__shelf-header">
              <h3>{shelf.name}</h3>
              <button type="button" onClick={() => onNavigate(shelf.id)}>
                Ver estantería
              </button>
            </header>
            <ShelfGrid
              compact
              slots={6}
              selectedIndex={
                selectedItem?.view === shelf.id ? selectedItem.index : null
              }
              onSelectItem={(index) => onSelectItem({ view: shelf.id, index })}
            />
          </section>
        ))}
      </div>
    </section>
  )
}
