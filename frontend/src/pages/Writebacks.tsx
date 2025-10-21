import { useQuery } from '@tanstack/react-query';
import { getMachines } from '../services/api';
import { HardDrive, AlertCircle, CheckCircle } from 'lucide-react';

const Writebacks = () => {
  const { data: machines, isLoading, error } = useQuery({
    queryKey: ['machines'],
    queryFn: getMachines,
    refetchInterval: 10000,
  });

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  if (isLoading) {
    return <div className="text-center py-12 text-gray-900 dark:text-gray-100">Loading writebacks...</div>;
  }

  if (error) {
    return (
      <div className="text-center py-12 text-red-600 dark:text-red-400">
        Error loading writebacks: {(error as Error).message}
      </div>
    );
  }

  const machinesWithWritebacks = machines?.filter((m) => m.writeback_size > 0) || [];

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 dark:text-gray-800">Writebacks</h1>
        <p className="text-gray-500 dark:text-gray-400 dark:text-gray-500 mt-1">
          Manage temporary write layers for client machines (
          {machinesWithWritebacks.length} active)
        </p>
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 dark:bg-blue-900 border border-blue-200 dark:border-blue-700 rounded-lg p-4 mb-6">
        <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">What are Writebacks?</h3>
        <p className="text-sm text-blue-800 dark:text-blue-200">
          Writebacks are temporary write layers that store changes made by client machines. They
          allow diskless clients to write data without modifying the base image. Writebacks can be
          kept (persistent) or discarded (reset to clean state) on reboot.
        </p>
      </div>

      {machinesWithWritebacks.length > 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                  Machine
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                  Image
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                  Writeback Size
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                  Persistence
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200">
              {machinesWithWritebacks.map((machine) => (
                <tr key={machine.id} className="hover:bg-gray-50 dark:bg-gray-800">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900 dark:text-gray-100 dark:text-gray-800">{machine.name}</div>
                    <div className="text-sm text-gray-500 dark:text-gray-400 dark:text-gray-500">{machine.mac_address}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 dark:text-gray-500">
                    {machine.image_name || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900 dark:text-gray-100 dark:text-gray-800">
                      {formatBytes(machine.writeback_size)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        machine.status === 'online'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {machine.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {machine.keep_writeback ? (
                      <div className="flex items-center gap-1 text-blue-600 dark:text-blue-400">
                        <CheckCircle size={16} />
                        <span className="text-sm font-medium">Keep</span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-1 text-gray-500 dark:text-gray-400">
                        <AlertCircle size={16} />
                        <span className="text-sm">Temporary</span>
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end gap-2">
                      <button className="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700 dark:bg-green-500 dark:hover:bg-green-600">
                        Apply
                      </button>
                      <button className="px-3 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700 dark:bg-red-500 dark:hover:bg-red-600">
                        Discard
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow">
          <HardDrive className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500 mb-4" />
          <p className="text-gray-600 dark:text-gray-400 dark:text-gray-500 mb-2">No active writebacks</p>
          <p className="text-sm text-gray-500 dark:text-gray-400 dark:text-gray-500">
            Writebacks are created automatically when diskless clients write data
          </p>
        </div>
      )}

      {/* Statistics */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <p className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-500">Total Writebacks</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-gray-100 dark:text-gray-800 mt-2">
            {machinesWithWritebacks.length}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <p className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-500">Total Writeback Size</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-gray-100 dark:text-gray-800 mt-2">
            {formatBytes(
              machinesWithWritebacks.reduce((sum, m) => sum + m.writeback_size, 0)
            )}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <p className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-500">Persistent Writebacks</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-gray-100 dark:text-gray-800 mt-2">
            {machinesWithWritebacks.filter((m) => m.keep_writeback).length}
          </p>
        </div>
      </div>
    </div>
  );
};

export default Writebacks;
