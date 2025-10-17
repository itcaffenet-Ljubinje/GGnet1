import { useState, useEffect } from 'react';
import { HardDrive, Database, AlertTriangle, CheckCircle } from 'lucide-react';

interface ArrayStatus {
  exists: boolean;
  health: string;
  type: string;
  devices: string[];
  capacity: {
    total_gb: number;
    used_gb: number;
    available_gb: number;
  };
}

const Storage = () => {
  const [arrayStatus, setArrayStatus] = useState<ArrayStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // TODO: Fetch from backend API /api/v1/storage/array/status
    // For now, use mock data
    setTimeout(() => {
      setArrayStatus({
        exists: true,
        health: 'healthy',
        type: 'RAID10',
        devices: ['sda', 'sdb', 'sdc', 'sdd'],
        capacity: {
          total_gb: 2000,
          used_gb: 450,
          available_gb: 1550,
        },
      });
      setLoading(false);
    }, 500);
  }, []);

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy':
        return 'text-green-600';
      case 'degraded':
        return 'text-yellow-600';
      case 'rebuilding':
        return 'text-blue-600';
      default:
        return 'text-red-600';
    }
  };

  const getHealthIcon = (health: string) => {
    switch (health) {
      case 'healthy':
        return <CheckCircle className="text-green-600" size={32} />;
      case 'degraded':
        return <AlertTriangle className="text-yellow-600" size={32} />;
      default:
        return <AlertTriangle className="text-red-600" size={32} />;
    }
  };

  if (loading) {
    return <div className="text-center py-12">Loading storage information...</div>;
  }

  const usagePercent = arrayStatus
    ? (arrayStatus.capacity.used_gb / arrayStatus.capacity.total_gb) * 100
    : 0;

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Storage & Array Management</h1>
        <p className="text-gray-500 mt-1">Manage RAID arrays, ZFS pools, and storage capacity</p>
      </div>

      {/* Array Health Status */}
      {arrayStatus && arrayStatus.exists ? (
        <>
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Array Health</h2>
              {getHealthIcon(arrayStatus.health)}
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Status:</span>
                <span className={`font-bold ${getHealthColor(arrayStatus.health)}`}>
                  {arrayStatus.health.toUpperCase()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Type:</span>
                <span className="font-medium">{arrayStatus.type}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Devices:</span>
                <span className="font-medium">{arrayStatus.devices.join(', ')}</span>
              </div>
            </div>
          </div>

          {/* Capacity */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-bold mb-4">Storage Capacity</h2>
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-2">
                <span>Used: {arrayStatus.capacity.used_gb} GB</span>
                <span>Available: {arrayStatus.capacity.available_gb} GB</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div
                  className={`h-4 rounded-full transition-all ${
                    usagePercent > 90
                      ? 'bg-red-500'
                      : usagePercent > 75
                      ? 'bg-yellow-500'
                      : 'bg-green-500'
                  }`}
                  style={{ width: `${usagePercent}%` }}
                />
              </div>
              <div className="flex justify-between text-sm mt-2">
                <span className="text-gray-600">
                  {usagePercent.toFixed(1)}% used
                </span>
                <span className="text-gray-600">
                  Total: {arrayStatus.capacity.total_gb} GB
                </span>
              </div>
            </div>
          </div>

          {/* Devices */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-bold mb-4">Physical Devices</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {arrayStatus.devices.map((device, index) => (
                <div
                  key={device}
                  className="p-4 border-2 border-green-200 bg-green-50 rounded-lg"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <HardDrive size={20} className="text-green-600" />
                    <span className="font-medium">/dev/{device}</span>
                  </div>
                  <div className="text-xs text-gray-600">
                    <p>Status: Active</p>
                    <p>Position: {index + 1} of {arrayStatus.devices.length}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Array Operations */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-bold mb-4">Array Operations</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button className="p-4 border-2 border-blue-200 rounded-lg hover:bg-blue-50 transition-colors text-left">
                <p className="font-medium text-blue-900">Add Device</p>
                <p className="text-sm text-gray-600">Expand array capacity</p>
              </button>
              <button className="p-4 border-2 border-yellow-200 rounded-lg hover:bg-yellow-50 transition-colors text-left">
                <p className="font-medium text-yellow-900">Rebuild Array</p>
                <p className="text-sm text-gray-600">After device failure</p>
              </button>
              <button className="p-4 border-2 border-purple-200 rounded-lg hover:bg-purple-50 transition-colors text-left">
                <p className="font-medium text-purple-900">Check Health</p>
                <p className="text-sm text-gray-600">Run diagnostics</p>
              </button>
            </div>
          </div>

          {/* ZFS Pool Info */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Database size={24} />
              ZFS Pool (Optional)
            </h2>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-800 mb-2">
                <strong>Note:</strong> If you're using ZFS instead of RAID10, the pool information will be displayed here.
              </p>
              <p className="text-sm text-blue-700">
                ZFS pools provide snapshots, compression, and better data integrity than traditional RAID.
              </p>
              <div className="mt-3">
                <code className="text-xs bg-blue-100 px-2 py-1 rounded">
                  zpool status pool0
                </code>
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <HardDrive className="mx-auto h-16 w-16 text-gray-400 mb-4" />
          <h3 className="text-xl font-bold text-gray-900 mb-2">No Array Detected</h3>
          <p className="text-gray-600 mb-6">
            No RAID array or ZFS pool detected. You need to create storage array first.
          </p>
          <div className="space-y-3 max-w-2xl mx-auto text-left">
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="font-medium text-blue-900 mb-2">Create RAID10 Array:</p>
              <code className="text-sm bg-white px-3 py-2 rounded block">
                sudo bash storage/raid/create_raid10.sh /dev/sda /dev/sdb /dev/sdc /dev/sdd
              </code>
            </div>
            <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <p className="font-medium text-purple-900 mb-2">Create ZFS Pool:</p>
              <code className="text-sm bg-white px-3 py-2 rounded block">
                sudo zpool create pool0 mirror /dev/sda /dev/sdb mirror /dev/sdc /dev/sdd
              </code>
            </div>
          </div>
        </div>
      )}

      {/* Management Scripts */}
      <div className="mt-6 bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">Management Scripts</h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium">Create RAID10 Array</p>
              <p className="text-sm text-gray-500">storage/raid/create_raid10.sh</p>
            </div>
            <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs rounded">Available</span>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium">Check Array Health</p>
              <p className="text-sm text-gray-500">storage/raid/check_array.sh</p>
            </div>
            <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs rounded">Available</span>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium">Array Manager (Python)</p>
              <p className="text-sm text-gray-500">storage/array_manager.py</p>
            </div>
            <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs rounded">Available</span>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium">RAM Cache Manager</p>
              <p className="text-sm text-gray-500">storage/cache/ram_cache_manager.py</p>
            </div>
            <span className="px-3 py-1 bg-green-100 text-green-800 text-xs rounded">Running</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Storage;

