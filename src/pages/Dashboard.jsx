import { MainLayout } from '../components/layout/MainLayout'
import { ShelfGrid } from '../features/shelves/ShelfGrid'
import './Dashboard.css'

export function Dashboard() {
  return (
    <MainLayout>
      <header className="dashboard__header">
        <h2 className="dashboard__title">Nombre de la Estantería</h2>
        <p className="dashboard__subtitle">Huecos vacíos — esqueleto visual</p>
      </header>
      <ShelfGrid />
    </MainLayout>
  )
}
