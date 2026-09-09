import './TopBar.css'

export function TopBar() {
  return (
    <header className="topbar">
      <form className="topbar__search-form" onSubmit={(event) => event.preventDefault()}>
        <label className="topbar__search">
          <span className="visually-hidden">Buscar en PLUTEA</span>
          <span className="topbar__icon" aria-hidden="true" />
          <input
            type="search"
            name="q"
            placeholder="Busca un título, un autor o algo como «juegos de mundo abierto»"
            autoComplete="off"
          />
        </label>
      </form>
    </header>
  )
}