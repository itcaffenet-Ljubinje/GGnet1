import { useState } from 'react';
import { Network as NetworkIcon, Server, Settings } from 'lucide-react';

const Network = () => {
  const [networkConfig, setNetworkConfig] = useState({
    dhcp_range_start: '192.168.1.100',
    dhcp_range_end: '192.168.1.200',
    subnet_mask: '255.255.255.0',
    gateway: '192.168.1.1',
    dns_servers: '8.8.8.8, 8.8.4.4',
    tftp_server: '192.168.1.10',
    nfs_server: '192.168.1.10',
    pxe_boot_enabled: true,
  });

  const handleSave = () => {
    // TODO: Implement actual network config save
    alert('Network configuration would be saved here.\nBackend endpoint /api/v1/network/config needs to be implemented.');
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Network Configuration</h1>
        <p className="text-gray-500 mt-1">Configure DHCP, TFTP, NFS, and PXE boot settings</p>
      </div>

      {/* PXE Boot Status */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">PXE Boot Status</h2>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={networkConfig.pxe_boot_enabled}
              onChange={(e) =>
                setNetworkConfig({
                  ...networkConfig,
                  pxe_boot_enabled: e.target.checked,
                })
              }
              className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
            <span className="text-sm font-medium">
              {networkConfig.pxe_boot_enabled ? 'Enabled' : 'Disabled'}
            </span>
          </label>
        </div>
        <div
          className={`p-4 rounded-lg ${
            networkConfig.pxe_boot_enabled ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'
          }`}
        >
          <p className="text-sm">
            {networkConfig.pxe_boot_enabled
              ? '✅ PXE boot is enabled. Clients can boot from network.'
              : '⚠️ PXE boot is disabled. Enable to allow network booting.'}
          </p>
        </div>
      </div>

      {/* DHCP Configuration */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <NetworkIcon size={24} />
          DHCP Configuration
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              DHCP Range Start
            </label>
            <input
              type="text"
              value={networkConfig.dhcp_range_start}
              onChange={(e) =>
                setNetworkConfig({ ...networkConfig, dhcp_range_start: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="192.168.1.100"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              DHCP Range End
            </label>
            <input
              type="text"
              value={networkConfig.dhcp_range_end}
              onChange={(e) =>
                setNetworkConfig({ ...networkConfig, dhcp_range_end: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="192.168.1.200"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Subnet Mask</label>
            <input
              type="text"
              value={networkConfig.subnet_mask}
              onChange={(e) =>
                setNetworkConfig({ ...networkConfig, subnet_mask: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="255.255.255.0"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Gateway</label>
            <input
              type="text"
              value={networkConfig.gateway}
              onChange={(e) =>
                setNetworkConfig({ ...networkConfig, gateway: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="192.168.1.1"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              DNS Servers (comma-separated)
            </label>
            <input
              type="text"
              value={networkConfig.dns_servers}
              onChange={(e) =>
                setNetworkConfig({ ...networkConfig, dns_servers: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="8.8.8.8, 8.8.4.4"
            />
          </div>
        </div>
      </div>

      {/* Boot Servers */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Server size={24} />
          Boot Servers
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              TFTP Server IP
            </label>
            <input
              type="text"
              value={networkConfig.tftp_server}
              onChange={(e) =>
                setNetworkConfig({ ...networkConfig, tftp_server: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="192.168.1.10"
            />
            <p className="text-xs text-gray-500 mt-1">
              TFTP server for iPXE boot scripts
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              NFS Server IP
            </label>
            <input
              type="text"
              value={networkConfig.nfs_server}
              onChange={(e) =>
                setNetworkConfig({ ...networkConfig, nfs_server: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="192.168.1.10"
            />
            <p className="text-xs text-gray-500 mt-1">
              NFS server for disk images and writebacks
            </p>
          </div>
        </div>
      </div>

      {/* Configuration Files */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Settings size={24} />
          Configuration Files
        </h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium">DHCP Configuration</p>
              <p className="text-sm text-gray-500">/etc/dhcp/dhcpd.conf</p>
            </div>
            <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">
              Generate
            </button>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium">TFTP Configuration</p>
              <p className="text-sm text-gray-500">/srv/ggnet/pxe/tftp/</p>
            </div>
            <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">
              View Files
            </button>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium">NFS Exports</p>
              <p className="text-sm text-gray-500">/etc/exports</p>
            </div>
            <button className="px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">
              Generate
            </button>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          Save Network Configuration
        </button>
      </div>
    </div>
  );
};

export default Network;
