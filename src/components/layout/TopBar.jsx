import './TopBar.css'

export function TopBar({ onSearch }) {
  function handleSubmit(event) {
    event.preventDefault()
    const query = new FormData(event.currentTarget).get('q')?.toString().trim()
    if (!query) return
    onSearch(query)
  }

  return (
    <header className="topbar">
      <form className="topbar__search-form" onSubmit={handleSubmit}>
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
