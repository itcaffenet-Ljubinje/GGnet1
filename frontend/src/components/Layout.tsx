import { Outlet, Link, useLocation } from 'react-router-dom'
import { Home, Monitor, HardDrive, Database, Camera, Network as NetworkIcon, Settings as SettingsIcon, Server, Moon, Sun } from 'lucide-react'
import { useDarkMode } from '../contexts/DarkModeContext'

const Layout = () => {
  const location = useLocation()
  const { isDarkMode, toggleDarkMode } = useDarkMode()

  const navigation = [
    { name: 'Dashboard', path: '/dashboard', icon: Home },
    { name: 'Machines', path: '/machines', icon: Monitor },
    { name: 'Images', path: '/images', icon: HardDrive },
    { name: 'Writebacks', path: '/writebacks', icon: Database },
    { name: 'Snapshots', path: '/snapshots', icon: Camera },
    { name: 'Storage', path: '/storage', icon: Server },
    { name: 'Network', path: '/network', icon: NetworkIcon },
    { name: 'Settings', path: '/settings', icon: SettingsIcon },
  ]

  const isActive = (path: string) => location.pathname === path

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-700 dark:bg-gray-900">
      {/* Sidebar */}
      <aside className="w-64 bg-white dark:bg-gray-800 dark:bg-gray-800 shadow-md">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-primary-600 dark:text-primary-400">ggNet</h1>
              <p className="text-sm text-gray-500 dark:text-gray-400 dark:text-gray-500 dark:text-gray-400">Diskless Boot Manager</p>
            </div>
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-lg hover:bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-700 transition-colors"
              title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              {isDarkMode ? <Sun size={20} className="text-yellow-500" /> : <Moon size={20} className="text-gray-600 dark:text-gray-400 dark:text-gray-500" />}
            </button>
          </div>
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
                    ? 'bg-primary-50 dark:bg-primary-900 text-primary-700 dark:text-primary-300 font-medium'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
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

