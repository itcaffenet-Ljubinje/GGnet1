/**
 * GGRock API Client Service
 * Handles all communication with the GGRock backend API
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  GGRockComputer,
  GGRockSession,
  GGRockUser,
  BootImage,
  SystemMetrics,
  AuthCredentials,
  AuthResponse,
  APIError,
  HealthStatus,
  ComputerAction,
  DeploymentRequest,
  GameLibraryItem,
  NetworkConfig,
  LicenseInfo,
} from '@/types/ggrock';

class GGRockAPIClient {
  private client: AxiosInstance;
  private authToken: string | null = null;
  private refreshToken: string | null = null;

  constructor(baseURL: string = import.meta.env.VITE_GGROCK_API_URL || 'http://localhost:5000') {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        if (this.authToken) {
          config.headers.Authorization = `Bearer ${this.authToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config;

        // Handle 401 errors (unauthorized)
        if (error.response?.status === 401 && originalRequest) {
          if (this.refreshToken) {
            try {
              await this.refreshAuthToken();
              return this.client(originalRequest);
            } catch (refreshError) {
              this.clearAuth();
              throw refreshError;
            }
          } else {
            this.clearAuth();
          }
        }

        return Promise.reject(this.handleError(error));
      }
    );

    // Load token from localStorage on initialization
    this.loadAuthFromStorage();
  }

  // ==================== Authentication ====================

  async authenticate(credentials: AuthCredentials): Promise<AuthResponse> {
    try {
      const response = await this.client.post<AuthResponse>('/auth/login', credentials);
      this.setAuth(response.data);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async refreshAuthToken(): Promise<void> {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await this.client.post<AuthResponse>('/auth/refresh', {
        refreshToken: this.refreshToken,
      });
      this.setAuth(response.data);
    } catch (error) {
      this.clearAuth();
      throw this.handleError(error);
    }
  }

  async logout(): Promise<void> {
    try {
      await this.client.post('/auth/logout');
    } finally {
      this.clearAuth();
    }
  }

  private setAuth(authData: AuthResponse): void {
    this.authToken = authData.token;
    this.refreshToken = authData.refreshToken || null;
    
    localStorage.setItem('ggrock_token', authData.token);
    if (authData.refreshToken) {
      localStorage.setItem('ggrock_refresh_token', authData.refreshToken);
    }
    localStorage.setItem('ggrock_user', JSON.stringify(authData.user));
  }

  private clearAuth(): void {
    this.authToken = null;
    this.refreshToken = null;
    localStorage.removeItem('ggrock_token');
    localStorage.removeItem('ggrock_refresh_token');
    localStorage.removeItem('ggrock_user');
  }

  private loadAuthFromStorage(): void {
    this.authToken = localStorage.getItem('ggrock_token');
    this.refreshToken = localStorage.getItem('ggrock_refresh_token');
  }

  isAuthenticated(): boolean {
    return this.authToken !== null;
  }

  getCurrentUser(): GGRockUser | null {
    const userStr = localStorage.getItem('ggrock_user');
    return userStr ? JSON.parse(userStr) : null;
  }

  // ==================== Computer Management ====================

  async getComputers(): Promise<GGRockComputer[]> {
    const response = await this.client.get<GGRockComputer[]>('/computers');
    return response.data;
  }

  async getComputer(id: string): Promise<GGRockComputer> {
    const response = await this.client.get<GGRockComputer>(`/computers/${id}`);
    return response.data;
  }

  async executeComputerAction(action: ComputerAction): Promise<void> {
    await this.client.post(`/computers/${action.computerId}/action`, {
      type: action.type,
      parameters: action.parameters,
    });
  }

  async rebootComputer(computerId: string): Promise<void> {
    await this.executeComputerAction({ type: 'reboot', computerId });
  }

  async shutdownComputer(computerId: string): Promise<void> {
    await this.executeComputerAction({ type: 'shutdown', computerId });
  }

  async wakeupComputer(computerId: string): Promise<void> {
    await this.executeComputerAction({ type: 'wakeup', computerId });
  }

  // ==================== Session Management ====================

  async getActiveSessions(): Promise<GGRockSession[]> {
    const response = await this.client.get<GGRockSession[]>('/sessions/active');
    return response.data;
  }

  async getAllSessions(): Promise<GGRockSession[]> {
    const response = await this.client.get<GGRockSession[]>('/sessions');
    return response.data;
  }

  async getSession(id: string): Promise<GGRockSession> {
    const response = await this.client.get<GGRockSession>(`/sessions/${id}`);
    return response.data;
  }

  async endSession(id: string): Promise<void> {
    await this.client.post(`/sessions/${id}/end`);
  }

  // ==================== Boot Management ====================

  async getBootImages(): Promise<BootImage[]> {
    const response = await this.client.get<BootImage[]>('/boot/images');
    return response.data;
  }

  async getBootImage(id: string): Promise<BootImage> {
    const response = await this.client.get<BootImage>(`/boot/images/${id}`);
    return response.data;
  }

  async deployBootImage(deployment: DeploymentRequest): Promise<void> {
    await this.client.post('/boot/deploy', deployment);
  }

  async setDefaultBootImage(imageId: string): Promise<void> {
    await this.client.post(`/boot/images/${imageId}/set-default`);
  }

  // ==================== System Metrics ====================

  async getSystemMetrics(): Promise<SystemMetrics> {
    const response = await this.client.get<SystemMetrics>('/metrics/system');
    return response.data;
  }

  async getComputerMetrics(computerId: string): Promise<any> {
    const response = await this.client.get(`/metrics/computers/${computerId}`);
    return response.data;
  }

  // ==================== User Management ====================

  async getUsers(): Promise<GGRockUser[]> {
    const response = await this.client.get<GGRockUser[]>('/users');
    return response.data;
  }

  async getUser(id: string): Promise<GGRockUser> {
    const response = await this.client.get<GGRockUser>(`/users/${id}`);
    return response.data;
  }

  async createUser(userData: Partial<GGRockUser>): Promise<GGRockUser> {
    const response = await this.client.post<GGRockUser>('/users', userData);
    return response.data;
  }

  async updateUser(id: string, userData: Partial<GGRockUser>): Promise<GGRockUser> {
    const response = await this.client.put<GGRockUser>(`/users/${id}`, userData);
    return response.data;
  }

  async deleteUser(id: string): Promise<void> {
    await this.client.delete(`/users/${id}`);
  }

  // ==================== Game Library ====================

  async getGames(): Promise<GameLibraryItem[]> {
    const response = await this.client.get<GameLibraryItem[]>('/games');
    return response.data;
  }

  async getGame(id: string): Promise<GameLibraryItem> {
    const response = await this.client.get<GameLibraryItem>(`/games/${id}`);
    return response.data;
  }

  // ==================== Network Configuration ====================

  async getNetworkConfig(): Promise<NetworkConfig> {
    const response = await this.client.get<NetworkConfig>('/network/config');
    return response.data;
  }

  async updateNetworkConfig(config: Partial<NetworkConfig>): Promise<NetworkConfig> {
    const response = await this.client.put<NetworkConfig>('/network/config', config);
    return response.data;
  }

  // ==================== License Management ====================

  async getLicenses(): Promise<LicenseInfo[]> {
    const response = await this.client.get<LicenseInfo[]>('/licenses');
    return response.data;
  }

  async getLicense(id: string): Promise<LicenseInfo> {
    const response = await this.client.get<LicenseInfo>(`/licenses/${id}`);
    return response.data;
  }

  // ==================== Health Check ====================

  async checkHealth(): Promise<HealthStatus> {
    const response = await this.client.get<HealthStatus>('/health');
    return response.data;
  }

  // ==================== Error Handling ====================

  private handleError(error: any): APIError {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<APIError>;
      if (axiosError.response?.data) {
        return axiosError.response.data;
      }
      return {
        code: 'NETWORK_ERROR',
        message: axiosError.message || 'Network error occurred',
        timestamp: new Date().toISOString(),
      };
    }

    return {
      code: 'UNKNOWN_ERROR',
      message: error.message || 'An unknown error occurred',
      timestamp: new Date().toISOString(),
    };
  }
}

// Export singleton instance
export const ggRockAPI = new GGRockAPIClient();
export default ggRockAPI;

