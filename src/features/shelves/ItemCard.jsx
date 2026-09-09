import './ItemCard.css'

export function ItemCard({ selected = false, onSelect }) {
  const className = selected ? 'item-card item-card--selected' : 'item-card'

  if (!onSelect) {
    return <div className={className} aria-hidden="true" />
  }

  return (
    <button
      type="button"
      className={className}
      onClick={onSelect}
      aria-pressed={selected}
      aria-label={selected ? 'Hueco seleccionado' : 'Abrir ficha del hueco'}
    />
  )
}
