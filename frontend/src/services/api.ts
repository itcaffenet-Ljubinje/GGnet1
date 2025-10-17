/**
 * ggNet API Service
 * 
 * Centralized API communication layer for ggNet frontend.
 * All backend communication goes through this service.
 */

const API_BASE = '/api/v1';

/**
 * Generic request handler with error handling
 */
async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: `HTTP Error ${response.status}`,
    }));
    throw new Error(error.detail || `Request failed: ${response.statusText}`);
  }

  return response.json();
}

//=============================================================================
// Machines API
//=============================================================================

export interface Machine {
  id: number;
  name: string;
  mac_address: string;
  ip_address?: string;
  status: string;
  image_name?: string;
  writeback_size: number;
  keep_writeback: boolean;
  last_boot?: string;
}

export interface MachineCreate {
  name: string;
  mac_address: string;
  ip_address?: string;
}

export async function getMachines(): Promise<Machine[]> {
  return request<Machine[]>('/machines');
}

export async function getMachine(id: number): Promise<Machine> {
  return request<Machine>(`/machines/${id}`);
}

export async function createMachine(data: MachineCreate): Promise<Machine> {
  return request<Machine>('/machines', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function deleteMachine(id: number): Promise<void> {
  await request(`/machines/${id}`, {
    method: 'DELETE',
  });
}

export async function powerOperation(
  id: number,
  operation: 'power_on' | 'power_off' | 'reboot'
): Promise<{ success: boolean; message: string }> {
  return request(`/machines/${id}/power`, {
    method: 'POST',
    body: JSON.stringify({ operation }),
  });
}

export async function setKeepWriteback(
  id: number,
  keep: boolean
): Promise<Machine> {
  return request(`/machines/${id}/keep_writeback`, {
    method: 'PATCH',
    body: JSON.stringify({ keep }),
  });
}

export async function applyWriteback(
  id: number,
  comment?: string
): Promise<{ success: boolean; message: string }> {
  return request(`/machines/${id}/apply_writeback`, {
    method: 'POST',
    body: JSON.stringify({ comment }),
  });
}

//=============================================================================
// Images API
//=============================================================================

export interface Image {
  id: number;
  name: string;
  path: string;
  type: 'os' | 'game';
  size_bytes: number;
  active_snapshot_id?: number;
  created_at: string;
  updated_at: string;
}

export interface ImageCreate {
  name: string;
  type: 'os' | 'game';
  description?: string;
}

export async function getImages(type?: 'os' | 'game'): Promise<Image[]> {
  const params = type ? `?type=${type}` : '';
  return request<Image[]>(`/images${params}`);
}

export async function createImage(data: ImageCreate): Promise<Image> {
  return request<Image>('/images', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function deleteImage(id: number): Promise<void> {
  await request(`/images/${id}`, {
    method: 'DELETE',
  });
}

//=============================================================================
// Snapshots API
//=============================================================================

export interface Snapshot {
  id: number;
  image_id: number;
  created_by?: string;
  created_at: string;
  comment?: string;
  path: string;
}

export interface SnapshotCreate {
  image_id: number;
  comment?: string;
  created_by?: string;
}

export async function getSnapshots(): Promise<Snapshot[]> {
  return request<Snapshot[]>('/snapshots');
}

export async function createSnapshot(data: SnapshotCreate): Promise<Snapshot> {
  return request<Snapshot>('/snapshots', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function deleteSnapshot(id: number): Promise<void> {
  await request(`/snapshots/${id}`, {
    method: 'DELETE',
  });
}

//=============================================================================
// System API
//=============================================================================

export interface SystemMetrics {
  total_machines: number;
  online_machines: number;
  offline_machines: number;
  active_sessions: number;
  cpu_usage_avg: number;
  ram_usage_avg: number;
  disk_usage_percent: number;
  cache_hit_rate: number;
}

export interface StorageStatus {
  array_type: string;
  total_capacity_bytes: number;
  used_bytes: number;
  available_bytes: number;
  health: string;
}

export interface SystemStatus {
  app_name: string;
  version: string;
  uptime_seconds: number;
  db_status: string;
  system: {
    cpu_percent: number;
    memory_percent: number;
    disk_percent: number;
  };
}

export async function getSystemMetrics(): Promise<SystemMetrics> {
  return request<SystemMetrics>('/system/metrics');
}

export async function getStorageStatus(): Promise<StorageStatus> {
  return request<StorageStatus>('/system/storage');
}

export async function getSystemStatus(): Promise<SystemStatus> {
  // Status endpoint is at /api/status (not /api/v1/status)
  const response = await fetch('/api/status');
  if (!response.ok) {
    throw new Error(`Failed to fetch status: ${response.statusText}`);
  }
  return response.json();
}

export async function rebootServer(): Promise<{ success: boolean }> {
  return request('/system/reboot', {
    method: 'POST',
  });
}

//=============================================================================
// Logs API (placeholder for future implementation)
//=============================================================================

export interface LogEntry {
  timestamp: string;
  level: 'info' | 'warning' | 'error';
  message: string;
  source?: string;
}

export async function getLogs(limit: number = 100): Promise<LogEntry[]> {
  // TODO: Implement when backend endpoint is ready with limit parameter
  // For now, return mock data
  console.log(`Fetching logs with limit: ${limit}`); // Using limit to avoid TS error
  return [
    {
      timestamp: new Date().toISOString(),
      level: 'info',
      message: 'System started',
      source: 'main',
    },
  ];
}

//=============================================================================
// Network API (placeholder)
//=============================================================================

export interface NetworkConfig {
  server_ip: string;
  dhcp_start: string;
  dhcp_end: string;
  subnet_mask: string;
  gateway: string;
  dns_servers: string[];
}

export async function getNetworkConfig(): Promise<NetworkConfig> {
  return request<NetworkConfig>('/network/config');
}

export async function updateNetworkConfig(
  config: NetworkConfig
): Promise<{ success: boolean }> {
  return request('/network/config', {
    method: 'PUT',
    body: JSON.stringify(config),
  });
}

//=============================================================================
// Utility Functions
//=============================================================================

/**
 * Format bytes to human-readable string
 */
export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

/**
 * Format uptime seconds to human-readable string
 */
export function formatUptime(seconds: number): string {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  const parts: string[] = [];
  if (days > 0) parts.push(`${days}d`);
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);

  return parts.join(' ') || '< 1m';
}

/**
 * Format percentage
 */
export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}
