import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getMachines,
  createMachine,
  deleteMachine,
  powerOperation,
  setKeepWriteback,
  Machine,
  MachineCreate,
} from '../services/api';
import { Plus, Power, PowerOff, Trash2, HardDrive } from 'lucide-react';

const Machines = () => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [newMachine, setNewMachine] = useState<MachineCreate>({
    name: '',
    mac_address: '',
    ip_address: '',
  });

  const queryClient = useQueryClient();

  // Fetch machines
  const { data: machines, isLoading, error } = useQuery({
    queryKey: ['machines'],
    queryFn: getMachines,
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  // Create machine mutation
  const createMutation = useMutation({
    mutationFn: createMachine,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['machines'] });
      setShowAddForm(false);
      setNewMachine({ name: '', mac_address: '', ip_address: '' });
      alert('Machine added successfully!');
    },
    onError: (error: Error) => {
      alert(`Failed to add machine: ${error.message}`);
    },
  });

  // Delete machine mutation
  const deleteMutation = useMutation({
    mutationFn: deleteMachine,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['machines'] });
      alert('Machine deleted successfully!');
    },
    onError: (error: Error) => {
      alert(`Failed to delete machine: ${error.message}`);
    },
  });

  // Power operation mutation
  const powerMutation = useMutation({
    mutationFn: ({ id, action }: { id: number; action: string }) =>
      powerOperation(id, action),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['machines'] });
    },
    onError: (error: Error) => {
      alert(`Power operation failed: ${error.message}`);
    },
  });

  // Keep writeback mutation
  const keepWritebackMutation = useMutation({
    mutationFn: ({ id, keep }: { id: number; keep: boolean }) =>
      setKeepWriteback(id, keep),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['machines'] });
    },
    onError: (error: Error) => {
      alert(`Failed to update writeback setting: ${error.message}`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMachine.name || !newMachine.mac_address) {
      alert('Name and MAC address are required!');
      return;
    }
    createMutation.mutate(newMachine);
  };

  const handleDelete = (id: number, name: string) => {
    if (window.confirm(`Delete machine "${name}"? This cannot be undone.`)) {
      deleteMutation.mutate(id);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'bg-green-100 text-green-800';
      case 'offline':
        return 'bg-gray-100 text-gray-800';
      case 'booting':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-red-100 text-red-800';
    }
  };

  if (isLoading) {
    return <div className="text-center py-12">Loading machines...</div>;
  }

  if (error) {
    return (
      <div className="text-center py-12 text-red-600">
        Error loading machines: {(error as Error).message}
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Machines</h1>
          <p className="text-gray-500 mt-1">
            Manage diskless client machines ({machines?.length || 0} total)
          </p>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus size={20} />
          Add Machine
        </button>
      </div>

      {/* Add Machine Form */}
      {showAddForm && (
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6 border-2 border-blue-500">
          <h2 className="text-xl font-bold mb-4">Add New Machine</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Machine Name *
                </label>
                <input
                  type="text"
                  value={newMachine.name}
                  onChange={(e) =>
                    setNewMachine({ ...newMachine, name: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., PC-001"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  MAC Address *
                </label>
                <input
                  type="text"
                  value={newMachine.mac_address}
                  onChange={(e) =>
                    setNewMachine({ ...newMachine, mac_address: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="AA:BB:CC:DD:EE:FF"
                  pattern="[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  IP Address (Optional)
                </label>
                <input
                  type="text"
                  value={newMachine.ip_address || ''}
                  onChange={(e) =>
                    setNewMachine({ ...newMachine, ip_address: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="192.168.1.100"
                />
              </div>
            </div>

            <div className="flex gap-2">
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {createMutation.isPending ? 'Adding...' : 'Add Machine'}
              </button>
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Machines List */}
      {machines && machines.length > 0 ? (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  MAC Address
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  IP Address
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Image
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Writeback
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {machines.map((machine) => (
                <tr key={machine.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {machine.name}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">{machine.mac_address}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">
                      {machine.ip_address || '-'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(
                        machine.status
                      )}`}
                    >
                      {machine.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {machine.image_name || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-500">
                        {machine.writeback_size > 0
                          ? `${(machine.writeback_size / 1024 / 1024).toFixed(1)} MB`
                          : '-'}
                      </span>
                      {machine.writeback_size > 0 && (
                        <button
                          onClick={() =>
                            keepWritebackMutation.mutate({
                              id: machine.id,
                              keep: !machine.keep_writeback,
                            })
                          }
                          className={`px-2 py-1 text-xs rounded ${
                            machine.keep_writeback
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                          }`}
                          title={machine.keep_writeback ? 'Will keep writeback' : 'Will discard on reboot'}
                        >
                          {machine.keep_writeback ? 'Keep' : 'Temp'}
                        </button>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end gap-2">
                      {machine.status === 'offline' && (
                        <button
                          onClick={() =>
                            powerMutation.mutate({ id: machine.id, action: 'on' })
                          }
                          className="p-2 text-green-600 hover:bg-green-50 rounded transition-colors"
                          title="Power On (WoL)"
                        >
                          <Power size={18} />
                        </button>
                      )}

                      {machine.status === 'online' && (
                        <button
                          onClick={() =>
                            powerMutation.mutate({ id: machine.id, action: 'off' })
                          }
                          className="p-2 text-yellow-600 hover:bg-yellow-50 rounded transition-colors"
                          title="Power Off"
                        >
                          <PowerOff size={18} />
                        </button>
                      )}

                      <button
                        onClick={() => handleDelete(machine.id, machine.name)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
                        title="Delete Machine"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <HardDrive className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <p className="text-gray-600 mb-4">No machines registered yet</p>
          <button
            onClick={() => setShowAddForm(true)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus size={20} />
            Add Your First Machine
          </button>
        </div>
      )}
    </div>
  );
};

export default Machines;
