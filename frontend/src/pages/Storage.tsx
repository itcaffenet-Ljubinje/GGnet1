import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  HardDrive, 
  AlertTriangle, 
  CheckCircle, 
  Plus, 
  RefreshCw,
  MoreVertical,
  Info,
  X
} from 'lucide-react';

interface Drive {
  device: string;
  serial: string;
  model: string;
  capacity_gb: number;
  status: 'online' | 'offline' | 'failed';
  position: number;
}

interface ArrayStatusData {
  exists: boolean;
  health: 'online' | 'offline' | 'degraded' | 'rebuilding';
  type: string;
  devices: Drive[];
  capacity: {
    total_gb: number;
    used_gb: number;
    available_gb: number;
    reserved_gb: number;
    reserved_percent: number;
  };
  breakdown: {
    system_images_gb: number;
    game_images_gb: number;
    writebacks_gb: number;
    snapshots_gb: number;
  };
}

const Storage = () => {
  const [showDriveDetails, setShowDriveDetails] = useState<string | null>(null);
  const [showConfigureMenu, setShowConfigureMenu] = useState(false);
  const [showAddStripeDialog, setShowAddStripeDialog] = useState(false);
  const [showAddDriveDialog, setShowAddDriveDialog] = useState(false);
  const [selectedStripe, setSelectedStripe] = useState<string | null>(null);
  const [selectedRaidType, setSelectedRaidType] = useState<string>('raid10');
  const [selectedDevices, setSelectedDevices] = useState<string[]>([]);
  const queryClient = useQueryClient();

  // Fetch array status
  const { data: arrayStatus, isLoading: loading } = useQuery<ArrayStatusData>({
    queryKey: ['array-status'],
    queryFn: async () => {
      const response = await fetch('/api/v1/storage/array/status');
      if (!response.ok) {
        throw new Error('Failed to fetch array status');
      }
      return response.json();
      
      /* Mock data backup
      return {
        exists: true,
        health: 'online' as const,
        type: 'RAID10',
        devices: [
          { device: 'sda', serial: 'S3Z1NX0K123456', model: 'Micron 5200 ECO 1.92TB', capacity_gb: 1920, status: 'online' as const, position: 1 },
          { device: 'sdb', serial: 'S3Z1NX0K123457', model: 'Micron 5200 ECO 1.92TB', capacity_gb: 1920, status: 'online' as const, position: 2 },
          { device: 'sdc', serial: 'S3Z1NX0K123458', model: 'Micron 5200 ECO 1.92TB', capacity_gb: 1920, status: 'online' as const, position: 3 },
          { device: 'sdd', serial: 'S3Z1NX0K123459', model: 'Micron 5200 ECO 1.92TB', capacity_gb: 1920, status: 'online' as const, position: 4 },
        ],
        capacity: {
          total_gb: 3840,
          used_gb: 1450,
          available_gb: 1766,
          reserved_gb: 624,
          reserved_percent: 16.25,
        },
        breakdown: {
          system_images_gb: 800,
          game_images_gb: 450,
          writebacks_gb: 120,
          snapshots_gb: 80,
        },
      };
      */
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Drive operations mutations (MUST be before early returns)
  const bringOfflineMutation = useMutation({
    mutationFn: async (device: string) => {
      const response = await fetch(`/api/v1/storage/array/drives/${device}/offline`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to bring drive offline');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['array-status'] });
      alert('Drive brought offline successfully');
    },
  });

  const bringOnlineMutation = useMutation({
    mutationFn: async (device: string) => {
      const response = await fetch(`/api/v1/storage/array/drives/${device}/online`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to bring drive online');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['array-status'] });
      alert('Drive brought online successfully. Array will rebuild.');
    },
  });

  // Add stripe mutation
  const addStripeMutation = useMutation({
    mutationFn: async ({ stripeNumber, raidType, devices }: { stripeNumber: number; raidType: string; devices: string[] }) => {
      const response = await fetch('/api/v1/storage/array/stripes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          stripe_number: stripeNumber,
          raid_type: raidType,
          devices: devices
        }),
      });
      if (!response.ok) throw new Error('Failed to add stripe');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['array-status'] });
      queryClient.invalidateQueries({ queryKey: ['available-drives'] });
      setShowAddStripeDialog(false);
      setSelectedDevices([]);
      setSelectedRaidType('raid10');
      alert('Stripe added successfully');
    },
  });

  // Add drive to stripe mutation
  const addDriveToStripeMutation = useMutation({
    mutationFn: async ({ stripe, drive }: { stripe: string; drive: string }) => {
      const response = await fetch(`/api/v1/storage/array/stripes/${stripe}/drives`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device: drive }),
      });
      if (!response.ok) throw new Error('Failed to add drive to stripe');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['array-status'] });
      setShowAddDriveDialog(false);
      setSelectedStripe(null);
      alert('Drive added to stripe successfully');
    },
  });

  // Fetch available drives
  const { data: availableDrives } = useQuery({
    queryKey: ['available-drives'],
    queryFn: async () => {
      const response = await fetch('/api/v1/storage/array/available-drives');
      if (!response.ok) {
        throw new Error('Failed to fetch available drives');
      }
      return response.json();
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Early returns (after all hooks)
  if (loading) {
    return <div className="text-center py-12">Loading storage information...</div>;
  }

  if (!arrayStatus) {
    return <div className="text-center py-12 text-red-600">Error loading array status</div>;
  }

  const getHealthIcon = (health: string) => {
    switch (health) {
      case 'online':
        return <CheckCircle className="text-green-600" size={32} />;
      case 'degraded':
        return <AlertTriangle className="text-yellow-600" size={32} />;
      case 'rebuilding':
        return <RefreshCw className="text-blue-600 animate-spin" size={32} />;
      default:
        return <AlertTriangle className="text-red-600" size={32} />;
    }
  };

  const getDriveStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'border-green-500 bg-green-50';
      case 'offline':
        return 'border-gray-400 bg-gray-50';
      case 'failed':
        return 'border-red-500 bg-red-50';
      default:
        return 'border-gray-300 bg-gray-50';
    }
  };

  const getDriveStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <CheckCircle className="text-green-600" size={20} />;
      case 'offline':
        return <AlertTriangle className="text-gray-600 dark:text-gray-400 dark:text-gray-500" size={20} />;
      case 'failed':
        return <AlertTriangle className="text-red-600" size={20} />;
      default:
        return <HardDrive className="text-gray-600 dark:text-gray-400 dark:text-gray-500" size={20} />;
    }
  };

  const usagePercent = arrayStatus
    ? (arrayStatus.capacity.used_gb / arrayStatus.capacity.total_gb) * 100
    : 0;

  const selectedDrive = arrayStatus.devices.find((d: Drive) => d.device === showDriveDetails);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 dark:text-gray-800">Array Management</h1>
        <p className="text-gray-500 dark:text-gray-400 dark:text-gray-500 mt-1">
          Manage RAID arrays, ZFS pools, and storage capacity
        </p>
      </div>

      {/* Array Health Status - ggNet Style */}
      {arrayStatus.exists ? (
        <>
          {/* Array Rebuilding Warning */}
          {arrayStatus.health === 'rebuilding' && (
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
              <div className="flex items-start">
                <AlertTriangle className="text-yellow-600 mt-1 mr-3" size={24} />
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-yellow-900 mb-2">
                    Array is Rebuilding
                  </h3>
                  <p className="text-yellow-800 mb-2">
                    <strong>WARNING:</strong> The array is currently rebuilding. During this period:
                  </p>
                  <ul className="list-disc list-inside text-yellow-800 space-y-1">
                    <li>There will be degraded performance</li>
                    <li>There is an increased risk of data loss</li>
                    <li><strong>DO NOT power off or reboot the server</strong></li>
                    <li><strong>DO NOT interrupt the rebuild operation</strong></li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Array Status Indicator */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                {getHealthIcon(arrayStatus.health)}
                <div>
                  <h2 className="text-xl font-bold">Array Status</h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-500">
                    {arrayStatus.health === 'online' && 'Array is healthy and operational'}
                    {arrayStatus.health === 'degraded' && 'Array is degraded - replace failed drive'}
                    {arrayStatus.health === 'rebuilding' && 'Array is rebuilding - do not power off'}
                    {arrayStatus.health === 'offline' && 'Array is offline'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <div className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-500">RAID Type</div>
                  <div className="text-2xl font-bold text-blue-600">{arrayStatus.type}</div>
                </div>
                <div className="relative">
                  <button
                    onClick={() => setShowConfigureMenu(!showConfigureMenu)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                  >
                    <RefreshCw size={18} />
                    Configure
                  </button>
                  {showConfigureMenu && (
                    <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-10">
                      <button
                        onClick={() => {
                          setShowConfigureMenu(false);
                          setShowAddStripeDialog(true);
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 dark:text-gray-600 hover:bg-gray-100 dark:bg-gray-700"
                      >
                        Add Stripe
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Array Usage Indicator - ggNet Style */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-bold mb-4">Array Usage</h2>
            
            {/* Usage Bar Chart */}
            <div className="mb-6">
              <div className="flex justify-between text-sm mb-2">
                <span className="font-medium">Total Capacity</span>
                <span className="font-bold">{arrayStatus.capacity.total_gb} GB</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-6 relative overflow-hidden">
                {/* Used space */}
                <div
                  className="h-6 bg-blue-600 absolute left-0"
                  style={{ width: `${usagePercent}%` }}
                />
                {/* Reserved space */}
                <div
                  className="h-6 bg-yellow-500 absolute"
                  style={{ 
                    left: `${usagePercent}%`,
                    width: `${arrayStatus.capacity.reserved_percent}%`
                  }}
                />
              </div>
              <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400 dark:text-gray-500 mt-2">
                <span>Used: {arrayStatus.capacity.used_gb} GB ({usagePercent.toFixed(1)}%)</span>
                <span>Reserved: {arrayStatus.capacity.reserved_gb} GB ({arrayStatus.capacity.reserved_percent.toFixed(1)}%)</span>
              </div>
            </div>

            {/* Breakdown */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="text-sm text-blue-700 mb-1">System Images</div>
                <div className="text-2xl font-bold text-blue-900">{arrayStatus.breakdown.system_images_gb} GB</div>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                <div className="text-sm text-purple-700 mb-1">Game Images</div>
                <div className="text-2xl font-bold text-purple-900">{arrayStatus.breakdown.game_images_gb} GB</div>
              </div>
              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <div className="text-sm text-green-700 mb-1">Writebacks</div>
                <div className="text-2xl font-bold text-green-900">{arrayStatus.breakdown.writebacks_gb} GB</div>
              </div>
              <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
                <div className="text-sm text-orange-700 mb-1">Snapshots</div>
                <div className="text-2xl font-bold text-orange-900">{arrayStatus.breakdown.snapshots_gb} GB</div>
              </div>
            </div>
          </div>

          {/* Drives List - ggNet Style */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Physical Drives</h2>
              <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                <Plus size={18} />
                Add Drive
              </button>
            </div>

            <div className="space-y-3">
              {arrayStatus.devices.map((drive: Drive) => (
                <div
                  key={drive.device}
                  className={`p-4 rounded-lg border-2 ${getDriveStatusColor(drive.status)}`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {getDriveStatusIcon(drive.status)}
                      <div>
                        <div className="font-medium text-gray-900 dark:text-gray-100 dark:text-gray-800">
                          /dev/{drive.device} - {drive.model}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-500">
                          Serial: {drive.serial} • {drive.capacity_gb} GB
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="px-3 py-1 bg-white dark:bg-gray-800 text-xs rounded-full font-medium">
                        Position {drive.position}
                      </span>
                      <button
                        onClick={() => setShowDriveDetails(drive.device)}
                        className="p-2 hover:bg-white dark:bg-gray-800 rounded transition-colors"
                        title="View Details"
                      >
                        <Info size={18} className="text-gray-600 dark:text-gray-400 dark:text-gray-500" />
                      </button>
                      <div className="relative">
                        <button
                          className="p-2 hover:bg-white dark:bg-gray-800 rounded transition-colors"
                          title="More Options"
                        >
                          <MoreVertical size={18} className="text-gray-600 dark:text-gray-400 dark:text-gray-500" />
                        </button>
                        {/* Dropdown menu */}
                        <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-10 hidden group-hover:block">
                          <button
                            onClick={() => setShowDriveDetails(drive.device)}
                            className="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 dark:text-gray-600 hover:bg-gray-100 dark:bg-gray-700"
                          >
                            View Details
                          </button>
                          {drive.status === 'online' && (
                            <button
                              onClick={() => bringOfflineMutation.mutate(drive.device)}
                              className="w-full text-left px-4 py-2 text-sm text-yellow-700 hover:bg-yellow-50"
                            >
                              Bring Offline
                            </button>
                          )}
                          {drive.status === 'offline' && (
                            <button
                              onClick={() => bringOnlineMutation.mutate(drive.device)}
                              className="w-full text-left px-4 py-2 text-sm text-green-700 hover:bg-green-50"
                            >
                              Bring Online
                            </button>
                          )}
                          {drive.status === 'failed' && (
                            <button
                              onClick={() => alert('Replace drive functionality coming soon!')}
                              className="w-full text-left px-4 py-2 text-sm text-blue-700 hover:bg-blue-50"
                            >
                              Replace Drive
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Add Stripe Dialog */}
          {showAddStripeDialog && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
                <div className="flex items-center justify-between p-6 border-b">
                  <h3 className="text-xl font-bold">Add Stripe</h3>
                  <button
                    onClick={() => {
                      setShowAddStripeDialog(false);
                      setSelectedDevices([]);
                      setSelectedRaidType('raid10');
                    }}
                    className="p-2 hover:bg-gray-100 dark:bg-gray-700 rounded transition-colors"
                  >
                    <X size={20} />
                  </button>
                </div>
                <div className="p-6 space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Stripe Number
                    </label>
                    <select
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                      defaultValue={0}
                    >
                      {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
                        <option key={num} value={num}>
                          Stripe {num}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      RAID Type
                    </label>
                    <select
                      value={selectedRaidType}
                      onChange={(e) => setSelectedRaidType(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    >
                      <option value="raid0">RAID0 (Striping)</option>
                      <option value="raid1">RAID1 (Mirroring)</option>
                      <option value="raid10">RAID10 (Striped Mirrors)</option>
                      <option value="mirror">ZFS Mirror</option>
                      <option value="raidz">ZFS RAIDZ (Single Parity)</option>
                      <option value="raidz2">ZFS RAIDZ2 (Double Parity)</option>
                    </select>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {selectedRaidType === 'raid0' && 'Min 2 disks - No fault tolerance'}
                      {selectedRaidType === 'raid1' && 'Min 2 disks - 1 disk fault tolerance'}
                      {selectedRaidType === 'raid10' && 'Min 4 disks - 1 disk per mirror fault tolerance'}
                      {selectedRaidType === 'mirror' && 'Min 2 disks - 1 disk fault tolerance'}
                      {selectedRaidType === 'raidz' && 'Min 3 disks - 1 disk fault tolerance'}
                      {selectedRaidType === 'raidz2' && 'Min 4 disks - 2 disk fault tolerance'}
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Select Devices ({selectedDevices.length} selected)
                    </label>
                    <div className="border border-gray-300 dark:border-gray-600 rounded-lg p-3 max-h-48 overflow-y-auto">
                      {availableDrives && availableDrives.length > 0 ? (
                        availableDrives.map((drive: any) => (
                          <label key={drive.device} className="flex items-center space-x-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded cursor-pointer">
                            <input
                              type="checkbox"
                              checked={selectedDevices.includes(drive.device)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setSelectedDevices([...selectedDevices, drive.device]);
                                } else {
                                  setSelectedDevices(selectedDevices.filter(d => d !== drive.device));
                                }
                              }}
                              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                            />
                            <span className="text-sm text-gray-900 dark:text-gray-100">
                              /dev/{drive.device} - {drive.model} ({drive.size})
                            </span>
                          </label>
                        ))
                      ) : (
                        <p className="text-sm text-gray-500 dark:text-gray-400">No available drives</p>
                      )}
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <button
                      onClick={() => {
                        const select = document.querySelector('select') as HTMLSelectElement;
                        const stripeNumber = parseInt(select.value);
                        if (selectedDevices.length === 0) {
                          alert('Please select at least one device');
                          return;
                        }
                        addStripeMutation.mutate({ stripeNumber, raidType: selectedRaidType, devices: selectedDevices });
                      }}
                      className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                      disabled={addStripeMutation.isPending || selectedDevices.length === 0}
                    >
                      {addStripeMutation.isPending ? 'Adding...' : 'Add Stripe'}
                    </button>
                    <button
                      onClick={() => {
                        setShowAddStripeDialog(false);
                        setSelectedDevices([]);
                        setSelectedRaidType('raid10');
                      }}
                      className="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Add Drive to Stripe Dialog */}
          {showAddDriveDialog && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4">
                <div className="flex items-center justify-between p-6 border-b">
                  <h3 className="text-xl font-bold">Add Drive to Stripe</h3>
                  <button
                    onClick={() => {
                      setShowAddDriveDialog(false);
                      setSelectedStripe(null);
                    }}
                    className="p-2 hover:bg-gray-100 dark:bg-gray-700 rounded transition-colors"
                  >
                    <X size={20} />
                  </button>
                </div>
                <div className="p-6 space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Select Drive
                    </label>
                    <select
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                      defaultValue=""
                    >
                      <option value="">-- Select a drive --</option>
                      {availableDrives && availableDrives.length > 0 ? (
                        availableDrives.map((drive: any) => (
                          <option key={drive.device} value={drive.device}>
                            /dev/{drive.device} - {drive.model} ({drive.size})
                          </option>
                        ))
                      ) : (
                        <option value="" disabled>No available drives</option>
                      )}
                    </select>
                  </div>
                  <div className="bg-yellow-50 dark:bg-yellow-900 border border-yellow-200 dark:border-yellow-700 rounded-lg p-4">
                    <p className="text-sm text-yellow-800 dark:text-yellow-200">
                      <strong>Note:</strong> Any drive added to a stripe must have a capacity larger than the size of the largest drive in your array.
                    </p>
                  </div>
                  <div className="flex gap-3">
                    <button
                      onClick={() => {
                        const select = document.querySelector('select') as HTMLSelectElement;
                        const drive = select.value;
                        if (drive && selectedStripe) {
                          addDriveToStripeMutation.mutate({ stripe: selectedStripe, drive });
                        }
                      }}
                      className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                      disabled={addDriveToStripeMutation.isPending}
                    >
                      {addDriveToStripeMutation.isPending ? 'Adding...' : 'Add Drive'}
                    </button>
                    <button
                      onClick={() => {
                        setShowAddDriveDialog(false);
                        setSelectedStripe(null);
                      }}
                      className="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Drive Details Modal */}
          {showDriveDetails && selectedDrive && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4">
                <div className="flex items-center justify-between p-6 border-b">
                  <h3 className="text-xl font-bold">Drive Details</h3>
                  <button
                    onClick={() => setShowDriveDetails(null)}
                    className="p-2 hover:bg-gray-100 dark:bg-gray-700 rounded transition-colors"
                  >
                    <X size={20} />
                  </button>
                </div>
                <div className="p-6 space-y-4">
                  <div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-500">Device</div>
                    <div className="font-medium">/dev/{selectedDrive.device}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-500">Model</div>
                    <div className="font-medium">{selectedDrive.model}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-500">Serial Number</div>
                    <div className="font-medium">{selectedDrive.serial}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-500">Capacity</div>
                    <div className="font-medium">{selectedDrive.capacity_gb} GB</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-500">Status</div>
                    <div className="font-medium capitalize">{selectedDrive.status}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-500">Position in Array</div>
                    <div className="font-medium">{selectedDrive.position} of {arrayStatus.devices.length}</div>
                  </div>
                </div>
                <div className="p-6 border-t flex gap-2">
                  <button
                    onClick={() => setShowDriveDetails(null)}
                    className="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 dark:text-gray-600 rounded-lg hover:bg-gray-300 transition-colors"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Array Operations */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Array Operations</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button className="p-4 border-2 border-blue-200 rounded-lg hover:bg-blue-50 transition-colors text-left">
                <p className="font-medium text-blue-900">Add Drive</p>
                <p className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-500">Expand array capacity</p>
              </button>
              <button className="p-4 border-2 border-yellow-200 rounded-lg hover:bg-yellow-50 transition-colors text-left">
                <p className="font-medium text-yellow-900">Replace Drive</p>
                <p className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-500">Replace failed drive</p>
              </button>
              <button className="p-4 border-2 border-purple-200 rounded-lg hover:bg-purple-50 transition-colors text-left">
                <p className="font-medium text-purple-900">Check Health</p>
                <p className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-500">Run diagnostics</p>
              </button>
            </div>
          </div>
        </>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">No Array Detected</h2>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                No RAID array or ZFS pool detected. Create a storage array to get started.
              </p>
            </div>
            <div className="relative">
              <button
                onClick={() => setShowConfigureMenu(!showConfigureMenu)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
              >
                <RefreshCw size={18} />
                Configure
              </button>
              {showConfigureMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-10">
                  <button
                    onClick={() => {
                      setShowConfigureMenu(false);
                      setShowAddStripeDialog(true);
                    }}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:bg-gray-700"
                  >
                    Add Stripe
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="space-y-4">
            <div className="p-4 bg-blue-50 dark:bg-blue-900 border border-blue-200 dark:border-blue-700 rounded-lg">
              <p className="font-medium text-blue-900 dark:text-blue-100 mb-2">Create RAID10 Array:</p>
              <code className="text-sm bg-white dark:bg-gray-800 px-3 py-2 rounded block text-gray-900 dark:text-gray-100">
                sudo bash storage/raid/create_raid10.sh /dev/sda /dev/sdb /dev/sdc /dev/sdd
              </code>
            </div>
            <div className="p-4 bg-purple-50 dark:bg-purple-900 border border-purple-200 dark:border-purple-700 rounded-lg">
              <p className="font-medium text-purple-900 dark:text-purple-100 mb-2">Create ZFS Pool:</p>
              <code className="text-sm bg-white dark:bg-gray-800 px-3 py-2 rounded block text-gray-900 dark:text-gray-100">
                sudo zpool create pool0 mirror /dev/sda /dev/sdb mirror /dev/sdc /dev/sdd
              </code>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Storage;
