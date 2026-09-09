import './Sidebar.css'

const PLACEHOLDER_SHELVES = ['Estantería 1', 'Estantería 2', 'Estantería 3']

export function Sidebar() {
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

      <nav className="sidebar__nav" aria-label="Estanterías">
        <p className="sidebar__label">Estanterías</p>
        <ul className="sidebar__list">
          {PLACEHOLDER_SHELVES.map((name) => (
            <li key={name}>
              <span className="sidebar__item">{name}</span>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  )
}
