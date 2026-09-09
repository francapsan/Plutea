import { ProfileAvatar } from './ProfileAvatar'
import { Sidebar } from './Sidebar'
import { TopBar } from './TopBar'
import './MainLayout.css'

export function MainLayout({ children, view, onNavigate, detail }) {
  return (
    <div className="main-layout">
      <Sidebar view={view} onNavigate={onNavigate} />
      <ProfileAvatar />
      <div className="main-layout__stage">
        <TopBar />
        <div className="main-layout__body">
          <main className="main-layout__content">{children}</main>
          {detail}
        </div>
      </div>
    </div>
  )
}
