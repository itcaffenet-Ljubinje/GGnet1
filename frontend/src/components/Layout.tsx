import { Outlet, Link, useLocation } from 'react-router-dom'
import { Home, Monitor, HardDrive, Database, Camera, Network as NetworkIcon, Settings as SettingsIcon } from 'lucide-react'

const Layout = () => {
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', path: '/dashboard', icon: Home },
    { name: 'Machines', path: '/machines', icon: Monitor },
    { name: 'Images', path: '/images', icon: HardDrive },
    { name: 'Writebacks', path: '/writebacks', icon: Database },
    { name: 'Snapshots', path: '/snapshots', icon: Camera },
    { name: 'Network', path: '/network', icon: NetworkIcon },
    { name: 'Settings', path: '/settings', icon: SettingsIcon },
  ]

  const isActive = (path: string) => location.pathname === path

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-md">
        <div className="p-4 border-b">
          <h1 className="text-2xl font-bold text-primary-600">ggNet</h1>
          <p className="text-sm text-gray-500">Diskless Boot Manager</p>
        </div>
        <nav className="p-4 space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive(item.path)
                    ? 'bg-primary-50 text-primary-700 font-medium'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Icon size={20} />
                <span>{item.name}</span>
              </Link>
            )
          })}
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <div className="max-w-7xl mx-auto p-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

export default Layout

