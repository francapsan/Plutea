import { useEffect, useState } from 'react'
import { fetchBook } from '../search/api'
import { PLACEHOLDER_SHELVES } from './placeholders'
import './ItemDetail.css'

export function ItemDetail({ item, collection, onAddToShelf, onClose }) {
  const [synopsis, setSynopsis] = useState(item?.description ?? null)
  const [loadingSynopsis, setLoadingSynopsis] = useState(false)
  const [shelfId, setShelfId] = useState(PLACEHOLDER_SHELVES[0].id)
  const [feedback, setFeedback] = useState('')

  useEffect(() => {
    setSynopsis(null)
    setFeedback('')
    setShelfId(PLACEHOLDER_SHELVES[0].id)

    const bookId = item?.id || (item?.external_id ? `open_library:${item.external_id}` : null)
    if (!bookId) return undefined

    let cancelled = false
    setLoadingSynopsis(true)
    fetchBook(bookId, item.description)
      .then((detail) => {
        if (!cancelled) {
          setSynopsis(detail.description || item.description || null)
        }
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setLoadingSynopsis(false)
      })

    return () => {
      cancelled = true
    }
  }, [item?.id, item?.external_id, item?.description])

  const hasContent = Boolean(item?.title)
  const alreadyOnShelf = Boolean(
    item && collection?.[shelfId]?.some((book) => book.id === item.id),
  )

  function handleAdd(event) {
    event.preventDefault()
    if (!item || alreadyOnShelf) return
    onAddToShelf(shelfId, { ...item, description: synopsis ?? item.description })
    const shelf = PLACEHOLDER_SHELVES.find((entry) => entry.id === shelfId)
    setFeedback(`Añadido a ${shelf?.name ?? 'la estantería'}`)
  }

  return (
    <aside className="item-detail" aria-label="Ficha de la obra">
      <header className="item-detail__header">
        <p className="item-detail__kicker">Libro</p>
        <button type="button" className="item-detail__close" onClick={onClose}>
          Cerrar
        </button>
      </header>

      {item?.image_url ? (
        <img
          className="item-detail__cover item-detail__cover--image"
          src={item.image_url}
          alt=""
          referrerPolicy="no-referrer"
        />
      ) : (
        <div className="item-detail__cover" aria-hidden="true" />
      )}

      {hasContent ? (
        <div className="item-detail__meta">
          <h3 className="item-detail__title">{item.title}</h3>
          {item.subtitle ? <p>{item.subtitle}</p> : null}
          {item.year ? <p>{item.year}</p> : null}
        </div>
      ) : (
        <div className="item-detail__fields">
          <div className="item-detail__line item-detail__line--title" />
          <div className="item-detail__line" />
          <div className="item-detail__line item-detail__line--short" />
        </div>
      )}

      {hasContent ? (
        <section className="item-detail__block">
          <h3>Sinopsis</h3>
          {loadingSynopsis && !synopsis ? (
            <p className="item-detail__synopsis item-detail__synopsis--muted">Cargando sinopsis…</p>
          ) : synopsis ? (
            <p className="item-detail__synopsis">{synopsis}</p>
          ) : (
            <p className="item-detail__synopsis item-detail__synopsis--muted">
              No hay sinopsis para esta obra.
            </p>
          )}
        </section>
      ) : (
        <section className="item-detail__block">
          <h3>Sinopsis</h3>
          <div className="item-detail__note">
            <span />
            <span />
            <span />
          </div>
        </section>
      )}

      {hasContent && onAddToShelf ? (
        <form className="item-detail__add" onSubmit={handleAdd}>
          <label>
            <span>Estantería</span>
            <select value={shelfId} onChange={(event) => setShelfId(event.target.value)}>
              {PLACEHOLDER_SHELVES.map((shelf) => (
                <option key={shelf.id} value={shelf.id}>
                  {shelf.name}
                </option>
              ))}
            </select>
          </label>
          <button type="submit" disabled={alreadyOnShelf}>
            {alreadyOnShelf ? 'Ya está en esta estantería' : 'Añadir a la estantería'}
          </button>
          {feedback ? <p className="item-detail__feedback">{feedback}</p> : null}
        </form>
      ) : null}
    </aside>
  )
}
