import { ItemCard } from './ItemCard'
import './ShelfGrid.css'

export function ShelfGrid({
  slots = 12,
  compact = false,
  selectedIndex = null,
  onSelectItem,
}) {
  return (
    <div className={compact ? 'shelf-grid shelf-grid--compact' : 'shelf-grid'}>
      {Array.from({ length: slots }, (_, index) => (
        <ItemCard
          key={index}
          selected={selectedIndex === index}
          onSelect={onSelectItem ? () => onSelectItem(index) : undefined}
        />
      ))}
    </div>
  )
}
