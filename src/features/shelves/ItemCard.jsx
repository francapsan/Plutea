import { useState } from 'react'
import './ItemCard.css'

export function ItemCard({ item, selected = false, onSelect }) {
  const [failedUrl, setFailedUrl] = useState(null)
  const coverUrl = item?.image_url && item.image_url !== failedUrl ? item.image_url : null
  const filled = Boolean(coverUrl || item?.title)
  const className = [
    'item-card',
    selected ? 'item-card--selected' : '',
    filled ? 'item-card--filled' : '',
  ]
    .filter(Boolean)
    .join(' ')

  const label = item?.title
    ? item.title
    : selected
      ? 'Hueco seleccionado'
      : 'Abrir ficha del hueco'

  const cover = coverUrl ? (
    <img
      src={coverUrl}
      alt=""
      referrerPolicy="no-referrer"
      onError={() => setFailedUrl(coverUrl)}
    />
  ) : null

  if (!onSelect) {
    return (
      <div className={className} aria-hidden="true">
        {cover}
      </div>
    )
  }

  return (
    <button
      type="button"
      className={className}
      onClick={onSelect}
      aria-pressed={selected}
      aria-label={label}
    >
      {cover}
    </button>
  )
}
