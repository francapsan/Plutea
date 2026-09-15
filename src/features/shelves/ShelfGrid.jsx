import { ItemCard } from './ItemCard'
import './ShelfGrid.css'

export function ShelfGrid({
  items,
  slots = 12,
  compact = false,
  selectedIndex = null,
  onSelectItem,
}) {
  const count = items ? items.length : slots

  return (
    <div className={compact ? 'shelf-grid shelf-grid--compact' : 'shelf-grid'}>
      {Array.from({ length: count }, (_, index) => (
        <ItemCard
          key={items?.[index]?.id ?? index}
          item={items?.[index]}
          selected={selectedIndex === index}
          onSelect={onSelectItem ? () => onSelectItem(index) : undefined}
        />
      ))}
    </div>
  )
}
