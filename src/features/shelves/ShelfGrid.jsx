import { ItemCard } from './ItemCard'
import './ShelfGrid.css'

export function ShelfGrid() {
  return (
    <div className="shelf-grid">
      {Array.from({ length: 12 }, (_, index) => (
        <ItemCard key={index} />
      ))}
    </div>
  )
}
