import { Sidebar } from './Sidebar'
import './MainLayout.css'

export function MainLayout({ children }) {
  return (
    <div className="main-layout">
      <Sidebar />
      <main className="main-layout__content">{children}</main>
    </div>
  )
}
