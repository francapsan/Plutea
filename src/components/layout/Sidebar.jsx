import { PLACEHOLDER_SHELVES, ROOM_VIEW } from '../../features/shelves/placeholders'
import './Sidebar.css'

export function Sidebar({ view, onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <div className="sidebar__mark" aria-hidden="true">
          <span />
          <span />
          <span />
        </div>
        <div>
          <h1 className="sidebar__title">PLUTEA</h1>
          <p className="sidebar__tagline">Your entertainment shelf.</p>
        </div>
      </div>

      <nav className="sidebar__nav" aria-label="Habitación">
        <p className="sidebar__label">Espacio</p>
        <ul className="sidebar__list">
          <li>
            <button
              type="button"
              className={
                view === ROOM_VIEW
                  ? 'sidebar__item sidebar__item--active'
                  : 'sidebar__item'
              }
              onClick={() => onNavigate(ROOM_VIEW)}
            >
              Mi Habitación
            </button>
          </li>
        </ul>
      </nav>

      <nav className="sidebar__nav" aria-label="Estanterías">
        <p className="sidebar__label">Estanterías</p>
        <ul className="sidebar__list">
          {PLACEHOLDER_SHELVES.map((shelf) => (
            <li key={shelf.id}>
              <button
                type="button"
                className={
                  view === shelf.id
                    ? 'sidebar__item sidebar__item--active'
                    : 'sidebar__item'
                }
                onClick={() => onNavigate(shelf.id)}
              >
                {shelf.name}
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  )
}
