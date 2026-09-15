import { useState } from 'react'
import { Dashboard } from './pages/Dashboard'
import {
  addBookToShelf,
  loadCollection,
  saveCollection,
} from './features/shelves/collection'
import { ROOM_VIEW, SEARCH_VIEW } from './features/shelves/placeholders'

function App() {
  const [view, setView] = useState(ROOM_VIEW)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedItem, setSelectedItem] = useState(null)
  const [collection, setCollection] = useState(loadCollection)

  function handleNavigate(nextView) {
    setView(nextView)
    setSelectedItem(null)
  }

  function handleSearch(query) {
    setSearchQuery(query)
    setView(SEARCH_VIEW)
    setSelectedItem(null)
  }

  function handleAddToShelf(shelfId, book) {
    setCollection((current) => {
      const next = addBookToShelf(current, shelfId, book)
      saveCollection(next)
      return next
    })
  }

  return (
    <Dashboard
      view={view}
      searchQuery={searchQuery}
      collection={collection}
      onNavigate={handleNavigate}
      onSearch={handleSearch}
      selectedItem={selectedItem}
      onSelectItem={setSelectedItem}
      onAddToShelf={handleAddToShelf}
    />
  )
}

export default App
