import { useQuery } from '@tanstack/react-query'
import { getMachines, Machine, formatBytes } from '@/services/api'
import { Monitor, Plus } from 'lucide-react'

const Machines = () => {
  const { data: machines, isLoading, error } = useQuery({
    queryKey: ['machines'],
    queryFn: getMachines,
  })

  if (isLoading) {
    return <div className="text-center py-12">Loading machines...</div>
  }

  if (error) {
    return (
      <div className="text-center py-12 text-red-600">
        Error loading machines: {(error as Error).message}
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Machines</h1>
          <p className="text-gray-500 mt-1">
            {machines?.length || 0} machines registered
          </p>
        </div>
        <button className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 flex items-center gap-2">
          <Plus size={20} />
          Add Machine
        </button>
      </div>

      {/* Machines Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Machine
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                IP Address
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Image
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Writeback
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {machines?.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                  <Monitor className="mx-auto mb-4 text-gray-400" size={48} />
                  <p className="font-medium">No machines registered yet</p>
                  <p className="text-sm mt-1">Click "Add Machine" to register your first machine</p>
                </td>
              </tr>
            ) : (
              machines?.map((machine: Machine) => (
                <tr key={machine.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <Monitor className="mr-3 text-gray-400" size={20} />
                      <div>
                        <div className="font-medium">{machine.name}</div>
                        <div className="text-sm text-gray-500">{machine.mac_address}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {machine.ip_address || <span className="text-gray-400">N/A</span>}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${
                        machine.status === 'online'
                          ? 'bg-green-100 text-green-800'
                          : machine.status === 'booting'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {machine.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {machine.image_name || <span className="text-gray-400">None</span>}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {machine.writeback_size > 0 ? (
                      <span>
                        {formatBytes(machine.writeback_size)}
                        {machine.keep_writeback && (
                          <span className="ml-1 text-xs text-blue-600">(keep)</span>
                        )}
                      </span>
                    ) : (
                      <span className="text-gray-400">None</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button className="text-blue-600 hover:text-blue-900">
                      Actions
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* TODO: Add machine creation modal */}
      {/* TODO: Add bulk operations */}
      {/* TODO: Add writeback apply/discard actions */}
    </div>
  )
}

export default Machines

