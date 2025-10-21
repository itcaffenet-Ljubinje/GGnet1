import { useQuery } from '@tanstack/react-query'
import { getSystemStatus, formatUptime } from '@/services/api'
import { Activity, Server, Clock, Database } from 'lucide-react'

const Dashboard = () => {
  const { data: status, isLoading, error } = useQuery({
    queryKey: ['system-status'],
    queryFn: getSystemStatus,
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  if (isLoading) {
    return <div className="text-center py-12 text-gray-900 dark:text-gray-100">Loading system status...</div>
  }

  if (error) {
    return (
      <div className="text-center py-12 text-red-600 dark:text-red-400">
        Error loading status: {(error as Error).message}
      </div>
    )
  }

  const stats = [
    {
      name: 'System Status',
      value: status?.db_status === 'connected' ? 'Online' : 'Error',
      icon: Server,
      color: status?.db_status === 'connected' ? 'bg-green-500' : 'bg-red-500',
    },
    {
      name: 'Uptime',
      value: status?.uptime_seconds ? formatUptime(status.uptime_seconds) : 'Unknown',
      icon: Clock,
      color: 'bg-blue-500',
    },
    {
      name: 'Database',
      value: status?.db_status || 'Unknown',
      icon: Database,
      color: 'bg-purple-500',
    },
    {
      name: 'Version',
      value: status?.version || '1.0.0',
      icon: Activity,
      color: 'bg-gray-500',
    },
  ]

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Dashboard</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Welcome to {status?.app_name || 'ggNet'}</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.name} className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-2">{stat.value}</p>
                </div>
                <div className={`${stat.color} rounded-full p-3`}>
                  <Icon className="text-white" size={24} />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* System Metrics */}
      {status?.system && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">System Resources</h2>
          <div className="grid grid-cols-3 gap-6">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">CPU Usage</p>
              <div className="flex items-center gap-3">
                <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all"
                    style={{ width: `${status.system.cpu_percent}%` }}
                  />
                </div>
                <span className="text-lg font-semibold w-16 text-right text-gray-900 dark:text-gray-100">
                  {status.system.cpu_percent.toFixed(1)}%
                </span>
              </div>
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Memory Usage</p>
              <div className="flex items-center gap-3">
                <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-purple-500 h-2 rounded-full transition-all"
                    style={{ width: `${status.system.memory_percent}%` }}
                  />
                </div>
                <span className="text-lg font-semibold w-16 text-right">
                  {status.system.memory_percent.toFixed(1)}%
                </span>
              </div>
            </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Disk Usage</p>
                <div className="flex items-center gap-3">
                  <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-orange-500 h-2 rounded-full transition-all"
                    style={{ width: `${status.system.disk_percent}%` }}
                  />
                </div>
                <span className="text-lg font-semibold w-16 text-right">
                  {status.system.disk_percent.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-left transition-colors">
            <p className="font-medium text-gray-900 dark:text-gray-100">Add Machine</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">Register new client</p>
          </button>
          <button className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-left transition-colors">
            <p className="font-medium text-gray-900 dark:text-gray-100">Upload Image</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">Add OS/game image</p>
          </button>
          <button className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-left transition-colors">
            <p className="font-medium text-gray-900 dark:text-gray-100">Generate PXE</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">Update boot configs</p>
          </button>
          <button className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-left transition-colors">
            <p className="font-medium text-gray-900 dark:text-gray-100">View Logs</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">System activity</p>
          </button>
        </div>
      </div>

      {/* TODO: Add recent activity feed */}
      {/* TODO: Add storage array health widget */}
      {/* TODO: Add cache statistics */}
    </div>
  )
}

export default Dashboard


