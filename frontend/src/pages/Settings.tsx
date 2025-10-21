import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Settings as SettingsIcon,
  Server,
  HardDrive,
  Shield,
  Bell,
  Activity,
  Save,
} from 'lucide-react';

const Settings = () => {
  const queryClient = useQueryClient();
  
  const [settings, setSettings] = useState({
    // General
    system_name: 'ggNet Server',
    timezone: 'UTC',
    auto_updates: false,
    dark_mode: false,
    release_stream: 'prod',

    // RAM Settings
    ram_cache_size_mb: 0, // 0 = auto
    max_ram_for_vms_mb: 0, // 0 = auto
    server_reserved_mb: 4096,

    // Array Settings (ggNet)
    reserved_disk_space_percent: 15,
    warning_threshold_percent: 85,

    // Snapshots and Writebacks Retention (ggNet)
    unutilized_snapshots_days: 30,
    unprotected_snapshots_count: 5,
    inactive_writebacks_hours: 168, // 7 days

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

  // Fetch settings
  const { data: _currentSettings } = useQuery({
    queryKey: ['settings'],
    queryFn: async () => {
      const response = await fetch('/api/v1/settings/');
      if (!response.ok) {
        throw new Error('Failed to fetch settings');
      }
      const data = await response.json();
      // Merge fetched settings with current state
      return {
        ...settings,
        ...data.general,
        ...data.ram,
        ...data.array,
        ...data.retention,
        ...data.storage,
        ...data.performance,
        ...data.security,
        ...data.notifications
      };
    },
  });

  // Save settings mutation
  const saveMutation = useMutation({
    mutationFn: async (newSettings: typeof settings) => {
      const response = await fetch('/api/v1/settings/', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          general: {
            system_name: newSettings.system_name,
            timezone: newSettings.timezone,
            auto_updates: newSettings.auto_updates,
            dark_mode: newSettings.dark_mode,
            release_stream: newSettings.release_stream,
          },
          ram: {
            maximize_size: newSettings.ram_cache_size_mb === 0,
            ram_cache_size_mb: newSettings.ram_cache_size_mb,
            max_ram_for_vms_mb: newSettings.max_ram_for_vms_mb,
            server_reserved_mb: newSettings.server_reserved_mb,
          },
          array: {
            reserved_disk_space_percent: newSettings.reserved_disk_space_percent,
            warning_threshold_percent: newSettings.warning_threshold_percent,
          },
          retention: {
            unutilized_snapshots_days: newSettings.unutilized_snapshots_days,
            unprotected_snapshots_count: newSettings.unprotected_snapshots_count,
            inactive_writebacks_hours: newSettings.inactive_writebacks_hours,
          },
          storage: {
            cache_size_mb: newSettings.cache_size_mb,
            image_compression: newSettings.image_compression,
            auto_cleanup_days: newSettings.auto_cleanup_days,
          },
          performance: {
            max_concurrent_boots: newSettings.max_concurrent_boots,
            writeback_cache_mb: newSettings.writeback_cache_mb,
            snapshot_retention_days: newSettings.snapshot_retention_days,
          },
          security: {
            require_auth: newSettings.require_auth,
            api_rate_limit: newSettings.api_rate_limit,
            enable_https: newSettings.enable_https,
          },
          notifications: {
            email_alerts: newSettings.email_alerts,
            slack_webhook: newSettings.slack_webhook,
            disk_alert_threshold: newSettings.disk_alert_threshold,
          }
        }),
      });
      if (!response.ok) {
        throw new Error('Failed to save settings');
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
      alert('Settings saved successfully!');
    },
    onError: (error: Error) => {
      alert(`Failed to save settings: ${error.message}`);
    },
  });

  const handleSave = () => {
    saveMutation.mutate(settings);
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 dark:text-gray-800">System Settings</h1>
        <p className="text-gray-500 dark:text-gray-400 dark:text-gray-500 mt-1">Configure ggNet system parameters</p>
      </div>

      <div className="space-y-6">
        {/* General Settings */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <SettingsIcon size={24} />
            General
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
                System Name
              </label>
              <input
                type="text"
                value={settings.system_name}
                onChange={(e) => setSettings({ ...settings, system_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">Timezone</label>
              <select
                value={settings.timezone}
                onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg"
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
              <label htmlFor="auto_updates" className="text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600">
                Enable automatic system updates
              </label>
            </div>
          </div>
        </div>

        {/* RAM Settings - ggNet Style */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Activity size={24} />
            RAM Settings
          </h2>
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="maximize_ram"
                checked={settings.ram_cache_size_mb === 0}
                onChange={(e) => setSettings({ ...settings, ram_cache_size_mb: e.target.checked ? 0 : 51200 })}
                className="w-4 h-4 text-blue-600 rounded"
              />
              <label htmlFor="maximize_ram" className="text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600">
                Maximize size (Recommended - ggNet manages RAM automatically)
              </label>
            </div>

            {settings.ram_cache_size_mb !== 0 && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
                    RAM Cache Size (MB)
                  </label>
                  <input
                    type="number"
                    value={settings.ram_cache_size_mb}
                    onChange={(e) => setSettings({ ...settings, ram_cache_size_mb: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg"
                    min="1024"
                    max="102400"
                    step="1024"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 dark:text-gray-500 mt-1">
                    Amount of memory used for high-speed temporary data caching
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
                    Maximum RAM for VMs (MB)
                  </label>
                  <input
                    type="number"
                    value={settings.max_ram_for_vms_mb}
                    onChange={(e) => setSettings({ ...settings, max_ram_for_vms_mb: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg"
                    min="1024"
                    max="32768"
                    step="1024"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 dark:text-gray-500 mt-1">
                    Amount of memory set aside for ggNet virtual machines
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
                    Server Reserved (MB)
                  </label>
                  <input
                    type="number"
                    value={settings.server_reserved_mb}
                    onChange={(e) => setSettings({ ...settings, server_reserved_mb: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg"
                    min="2048"
                    max="8192"
                    step="512"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 dark:text-gray-500 mt-1">
                    Amount of memory reserved for the Operating System and critical processes
                  </p>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Array and Images Settings - ggNet Style */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <HardDrive size={24} />
            Array and Images
          </h2>
          
          {/* Array Settings */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3 text-gray-800 dark:text-gray-200 dark:text-gray-700">Array Settings</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
                  Reserved disk space (%)
                </label>
                <input
                  type="number"
                  value={settings.reserved_disk_space_percent}
                  onChange={(e) => setSettings({ ...settings, reserved_disk_space_percent: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg"
                  min="10"
                  max="30"
                  step="1"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 dark:text-gray-500 mt-1">
                  <strong>Recommended: 15%</strong> - Critical for SSD performance. Performance decreases as drives fill up due to TRIM/erase operations.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
                  Warning threshold (%)
                </label>
                <input
                  type="number"
                  value={settings.warning_threshold_percent}
                  onChange={(e) => setSettings({ ...settings, warning_threshold_percent: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg"
                  min="70"
                  max="95"
                  step="5"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 dark:text-gray-500 mt-1">
                  Disk space warning threshold - you'll be notified when usage exceeds this value
                </p>
              </div>
            </div>
          </div>

          {/* Snapshots and Writebacks Retention Settings */}
          <div>
            <h3 className="text-lg font-semibold mb-3 text-gray-800 dark:text-gray-200 dark:text-gray-700">Snapshots and Writebacks Retention Settings</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
                  Unutilized Snapshots (days)
                </label>
                <input
                  type="number"
                  value={settings.unutilized_snapshots_days}
                  onChange={(e) => setSettings({ ...settings, unutilized_snapshots_days: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg"
                  min="7"
                  max="90"
                  step="1"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 dark:text-gray-500 mt-1">
                  How long to retain snapshots that have not been activated (eligible for deletion unless protected)
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
                  Unprotected Snapshots (count)
                </label>
                <input
                  type="number"
                  value={settings.unprotected_snapshots_count}
                  onChange={(e) => setSettings({ ...settings, unprotected_snapshots_count: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg"
                  min="3"
                  max="20"
                  step="1"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 dark:text-gray-500 mt-1">
                  Number of snapshots to keep even if they are eligible for deletion based on age
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
                  Inactive Writebacks (hours)
                </label>
                <input
                  type="number"
                  value={settings.inactive_writebacks_hours}
                  onChange={(e) => setSettings({ ...settings, inactive_writebacks_hours: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg"
                  min="24"
                  max="720"
                  step="24"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 dark:text-gray-500 mt-1">
                  How long to retain writebacks for powered-off systems (prevents unnecessary writebacks from consuming disk space)
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Storage Settings */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <HardDrive size={24} />
            Storage Settings
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
                RAM Cache Size (MB)
              </label>
              <input
                type="number"
                value={settings.cache_size_mb}
                onChange={(e) =>
                  setSettings({ ...settings, cache_size_mb: parseInt(e.target.value) })
                }
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg"
                min="1024"
                max="102400"
                step="1024"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 dark:text-gray-500 mt-1">
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
              <label htmlFor="image_compression" className="text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600">
                Enable image compression (saves space, slower boot)
              </label>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
                Auto-cleanup old writebacks after (days)
              </label>
              <input
                type="number"
                value={settings.auto_cleanup_days}
                onChange={(e) =>
                  setSettings({ ...settings, auto_cleanup_days: parseInt(e.target.value) })
                }
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg"
                min="1"
                max="365"
              />
            </div>
          </div>
        </div>

        {/* Performance Settings */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Server size={24} />
            Performance Settings
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
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
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg"
                min="1"
                max="200"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 dark:text-gray-500 mt-1">
                How many clients can boot simultaneously
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
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
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg"
                min="512"
                max="8192"
                step="512"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
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
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg"
                min="7"
                max="365"
              />
            </div>
          </div>
        </div>

        {/* Security Settings */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
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
              <label htmlFor="require_auth" className="text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600">
                Require authentication for API access
              </label>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
                API Rate Limit (requests/hour)
              </label>
              <input
                type="number"
                value={settings.api_rate_limit}
                onChange={(e) =>
                  setSettings({ ...settings, api_rate_limit: parseInt(e.target.value) })
                }
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg"
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
              <label htmlFor="enable_https" className="text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600">
                Enable HTTPS (requires SSL certificate)
              </label>
            </div>
          </div>
        </div>

        {/* Notification Settings */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
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
              <label htmlFor="email_alerts" className="text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600">
                Enable email alerts
              </label>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
                Slack Webhook URL (Optional)
              </label>
              <input
                type="text"
                value={settings.slack_webhook}
                onChange={(e) =>
                  setSettings({ ...settings, slack_webhook: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg"
                placeholder="https://hooks.slack.com/services/..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 dark:text-gray-600 mb-2">
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
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg"
                min="50"
                max="95"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 dark:text-gray-500 mt-1">
                Alert when disk usage exceeds this percentage
              </p>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end gap-4">
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 dark:text-gray-600 rounded-lg hover:bg-gray-300 transition-colors font-medium"
          >
            Reset to Defaults
          </button>
          <button
            onClick={handleSave}
            disabled={saveMutation.isPending}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50"
          >
            <Save size={20} />
            {saveMutation.isPending ? 'Saving...' : 'Apply Changes'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
