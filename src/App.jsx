import { useState } from 'react'
import { Dashboard } from './pages/Dashboard'
import { ROOM_VIEW } from './features/shelves/placeholders'

function App() {
  const [view, setView] = useState(ROOM_VIEW)
  const [selectedItem, setSelectedItem] = useState(null)

  function handleNavigate(nextView) {
    setView(nextView)
    setSelectedItem(null)
  }

  return (
    <Dashboard
      view={view}
      onNavigate={handleNavigate}
      selectedItem={selectedItem}
      onSelectItem={setSelectedItem}
    />
  )
}

export default App
