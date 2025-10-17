const Settings = () => {
  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">System Settings</h1>
      
      <div className="space-y-6">
        {/* Storage Settings */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Storage Configuration</h2>
          <p className="text-gray-600 mb-4">Configure storage arrays and paths</p>
          {/* TODO: Storage path configuration */}
          {/* TODO: RAID/ZFS array setup wizard */}
        </div>

        {/* RAM Cache Settings */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">RAM Cache</h2>
          <p className="text-gray-600 mb-4">Configure RAM cache for image acceleration</p>
          {/* TODO: RAM cache size slider */}
          {/* TODO: Preload image selection */}
        </div>

        {/* Retention Policies */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Retention Policies</h2>
          <p className="text-gray-600 mb-4">Configure automatic cleanup of writebacks and snapshots</p>
          {/* TODO: Writeback retention hours */}
          {/* TODO: Snapshot retention days */}
        </div>

        {/* System Actions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">System Actions</h2>
          <div className="space-x-4">
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
              Restart Services
            </button>
            <button className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700">
              Reboot Server
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings

