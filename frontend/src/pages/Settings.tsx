import { useState } from 'react';
import {
  Settings as SettingsIcon,
  Server,
  Database,
  HardDrive,
  Clock,
  Shield,
  Bell,
} from 'lucide-react';

const Settings = () => {
  const [settings, setSettings] = useState({
    // General
    system_name: 'ggNet Server',
    timezone: 'UTC',
    auto_updates: false,

    // Storage
    cache_size_mb: 51200,
    image_compression: true,
    auto_cleanup_days: 30,

    // Performance
    max_concurrent_boots: 50,
    writeback_cache_mb: 2048,
    snapshot_retention_days: 90,

    // Security
    require_auth: false,
    api_rate_limit: 1000,
    enable_https: false,

    // Notifications
    email_alerts: false,
    slack_webhook: '',
    disk_alert_threshold: 90,
  });

  const handleSave = () => {
    // TODO: Implement actual settings save
    alert('Settings would be saved here.\nBackend endpoint /api/v1/settings needs to be implemented.');
    console.log('Settings to save:', settings);
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">System Settings</h1>
        <p className="text-gray-500 mt-1">Configure ggNet system parameters</p>
      </div>

      <div className="space-y-6">
        {/* General Settings */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <SettingsIcon size={24} />
            General Settings
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                System Name
              </label>
              <input
                type="text"
                value={settings.system_name}
                onChange={(e) => setSettings({ ...settings, system_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Timezone</label>
              <select
                value={settings.timezone}
                onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="UTC">UTC</option>
                <option value="Europe/Belgrade">Europe/Belgrade</option>
                <option value="Europe/London">Europe/London</option>
                <option value="America/New_York">America/New_York</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="auto_updates"
                checked={settings.auto_updates}
                onChange={(e) => setSettings({ ...settings, auto_updates: e.target.checked })}
                className="w-4 h-4 text-blue-600 rounded"
              />
              <label htmlFor="auto_updates" className="text-sm font-medium text-gray-700">
                Enable automatic system updates
              </label>
            </div>
          </div>
        </div>

        {/* Storage Settings */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <HardDrive size={24} />
            Storage Settings
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                RAM Cache Size (MB)
              </label>
              <input
                type="number"
                value={settings.cache_size_mb}
                onChange={(e) =>
                  setSettings({ ...settings, cache_size_mb: parseInt(e.target.value) })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                min="1024"
                max="102400"
                step="1024"
              />
              <p className="text-xs text-gray-500 mt-1">
                Recommended: 50-75% of available RAM
              </p>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="image_compression"
                checked={settings.image_compression}
                onChange={(e) =>
                  setSettings({ ...settings, image_compression: e.target.checked })
                }
                className="w-4 h-4 text-blue-600 rounded"
              />
              <label htmlFor="image_compression" className="text-sm font-medium text-gray-700">
                Enable image compression (saves space, slower boot)
              </label>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Auto-cleanup old writebacks after (days)
              </label>
              <input
                type="number"
                value={settings.auto_cleanup_days}
                onChange={(e) =>
                  setSettings({ ...settings, auto_cleanup_days: parseInt(e.target.value) })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                min="1"
                max="365"
              />
            </div>
          </div>
        </div>

        {/* Performance Settings */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Server size={24} />
            Performance Settings
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Concurrent Boots
              </label>
              <input
                type="number"
                value={settings.max_concurrent_boots}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    max_concurrent_boots: parseInt(e.target.value),
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                min="1"
                max="200"
              />
              <p className="text-xs text-gray-500 mt-1">
                How many clients can boot simultaneously
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Writeback Cache (MB)
              </label>
              <input
                type="number"
                value={settings.writeback_cache_mb}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    writeback_cache_mb: parseInt(e.target.value),
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                min="512"
                max="8192"
                step="512"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Snapshot Retention (days)
              </label>
              <input
                type="number"
                value={settings.snapshot_retention_days}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    snapshot_retention_days: parseInt(e.target.value),
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                min="7"
                max="365"
              />
            </div>
          </div>
        </div>

        {/* Security Settings */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Shield size={24} />
            Security Settings
          </h2>
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="require_auth"
                checked={settings.require_auth}
                onChange={(e) =>
                  setSettings({ ...settings, require_auth: e.target.checked })
                }
                className="w-4 h-4 text-blue-600 rounded"
              />
              <label htmlFor="require_auth" className="text-sm font-medium text-gray-700">
                Require authentication for API access
              </label>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Rate Limit (requests/hour)
              </label>
              <input
                type="number"
                value={settings.api_rate_limit}
                onChange={(e) =>
                  setSettings({ ...settings, api_rate_limit: parseInt(e.target.value) })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                min="100"
                max="10000"
                step="100"
              />
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="enable_https"
                checked={settings.enable_https}
                onChange={(e) =>
                  setSettings({ ...settings, enable_https: e.target.checked })
                }
                className="w-4 h-4 text-blue-600 rounded"
              />
              <label htmlFor="enable_https" className="text-sm font-medium text-gray-700">
                Enable HTTPS (requires SSL certificate)
              </label>
            </div>
          </div>
        </div>

        {/* Notification Settings */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Bell size={24} />
            Notifications
          </h2>
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="email_alerts"
                checked={settings.email_alerts}
                onChange={(e) =>
                  setSettings({ ...settings, email_alerts: e.target.checked })
                }
                className="w-4 h-4 text-blue-600 rounded"
              />
              <label htmlFor="email_alerts" className="text-sm font-medium text-gray-700">
                Enable email alerts
              </label>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Slack Webhook URL (Optional)
              </label>
              <input
                type="text"
                value={settings.slack_webhook}
                onChange={(e) =>
                  setSettings({ ...settings, slack_webhook: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="https://hooks.slack.com/services/..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Disk Space Alert Threshold (%)
              </label>
              <input
                type="number"
                value={settings.disk_alert_threshold}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    disk_alert_threshold: parseInt(e.target.value),
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                min="50"
                max="95"
              />
              <p className="text-xs text-gray-500 mt-1">
                Alert when disk usage exceeds this percentage
              </p>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end gap-4">
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
          >
            Reset to Defaults
          </button>
          <button
            onClick={handleSave}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Save All Settings
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
