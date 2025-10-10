/**
 * GGRock API Type Definitions
 * Based on GGRock v0.1.2200.2324-1 Integration Analysis
 */

export type ComputerStatus = 'online' | 'offline' | 'booting' | 'error' | 'maintenance';
export type SessionStatus = 'active' | 'paused' | 'ended';
export type BootImageType = 'windows' | 'linux' | 'custom';

export interface GGRockComputer {
  id: string;
  hostname: string;
  macAddress: string;
  ipAddress: string;
  status: ComputerStatus;
  bootImage: string;
  bootImageId?: string;
  lastSeen: Date | string;
  cpuUsage?: number;
  memoryUsage?: number;
  diskUsage?: number;
  temperature?: number;
  uptime?: number;
  hardwareInfo?: HardwareInfo;
}

export interface HardwareInfo {
  cpu: string;
  ram: string;
  gpu?: string;
  storage?: string;
  motherboard?: string;
  manufacturer?: string;
  model?: string;
  serialNumber?: string;
}

export interface GGRockSession {
  id: string;
  userId: string;
  username: string;
  computerId: string;
  computerName: string;
  status: SessionStatus;
  startTime: Date | string;
  endTime?: Date | string;
  duration: number;
  currentGame?: string;
  ipAddress?: string;
}

export interface GGRockUser {
  id: string;
  username: string;
  email: string;
  firstName?: string;
  lastName?: string;
  role: UserRole;
  createdAt: Date | string;
  lastLogin?: Date | string;
  balance?: number;
  timeRemaining?: number;
  isActive: boolean;
  permissions: string[];
}

export type UserRole = 'admin' | 'operator' | 'user' | 'guest';

export interface BootImage {
  id: string;
  name: string;
  description?: string;
  type: BootImageType;
  version: string;
  size: number;
  path: string;
  createdAt: Date | string;
  updatedAt: Date | string;
  isDefault: boolean;
  installedGames?: string[];
  installedSoftware?: string[];
}

export interface SystemMetrics {
  timestamp: Date | string;
  totalComputers: number;
  onlineComputers: number;
  offlineComputers: number;
  activeSessions: number;
  cpuUsageAverage: number;
  memoryUsageAverage: number;
  networkTraffic: NetworkTraffic;
  diskUsage: DiskUsage;
}

export interface NetworkTraffic {
  incoming: number; // bytes per second
  outgoing: number; // bytes per second
}

export interface DiskUsage {
  total: number; // bytes
  used: number; // bytes
  free: number; // bytes
  percentage: number;
}

export interface AuthCredentials {
  username: string;
  password: string;
}

export interface AuthResponse {
  token: string;
  refreshToken?: string;
  user: GGRockUser;
  expiresIn: number;
}

export interface APIError {
  code: string;
  message: string;
  details?: any;
  timestamp: Date | string;
}

export interface HealthStatus {
  status: 'healthy' | 'unhealthy' | 'degraded';
  timestamp: Date | string;
  services?: ServiceHealth[];
  error?: string;
}

export interface ServiceHealth {
  name: string;
  status: 'up' | 'down';
  responseTime?: number;
  lastCheck: Date | string;
}

export interface WebSocketMessage<T = any> {
  type: string;
  payload: T;
  timestamp: Date | string;
}

export interface ComputerAction {
  type: 'reboot' | 'shutdown' | 'wakeup' | 'deploy_image';
  computerId: string;
  parameters?: any;
}

export interface DeploymentRequest {
  imageId: string;
  computerIds: string[];
  scheduleTime?: Date | string;
  forceReboot?: boolean;
}

export interface GameLibraryItem {
  id: string;
  name: string;
  publisher?: string;
  version?: string;
  installPath: string;
  size: number;
  icon?: string;
  executablePath: string;
  bootImages: string[]; // Boot image IDs that have this game
}

export interface NetworkConfig {
  dhcpEnabled: boolean;
  ipRange: {
    start: string;
    end: string;
  };
  subnet: string;
  gateway: string;
  dns: string[];
  vlanId?: number;
}

export interface LicenseInfo {
  id: string;
  softwareName: string;
  licenseKey: string;
  type: 'perpetual' | 'subscription' | 'trial';
  expiryDate?: Date | string;
  seats: number;
  usedSeats: number;
  isActive: boolean;
}

