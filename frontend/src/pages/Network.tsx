const Network = () => {
  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Network Configuration</h1>
      <div className="bg-white rounded-lg shadow p-6 space-y-6">
        <div>
          <h2 className="text-xl font-semibold mb-4">DHCP Settings</h2>
          <p className="text-gray-600">Configure DHCP range and PXE boot options</p>
          {/* TODO: DHCP configuration form */}
        </div>
        <div>
          <h2 className="text-xl font-semibold mb-4">Active Leases</h2>
          <p className="text-gray-600">View current DHCP leases</p>
          {/* TODO: DHCP lease table */}
        </div>
      </div>
    </div>
  )
}

export default Network

