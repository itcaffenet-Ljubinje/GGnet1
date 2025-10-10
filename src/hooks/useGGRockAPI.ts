/**
 * React Query hooks for GGRock API
 * Provides caching, loading states, and error handling
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ggRockAPI } from '@/services/ggrock-api';
import type {
  GGRockComputer,
  GGRockSession,
  GGRockUser,
  BootImage,
  SystemMetrics,
  AuthCredentials,
  ComputerAction,
  DeploymentRequest,
  GameLibraryItem,
  NetworkConfig,
  LicenseInfo,
} from '@/types/ggrock';

// Query Keys
export const queryKeys = {
  computers: ['computers'] as const,
  computer: (id: string) => ['computers', id] as const,
  sessions: ['sessions'] as const,
  activeSessions: ['sessions', 'active'] as const,
  session: (id: string) => ['sessions', id] as const,
  bootImages: ['boot-images'] as const,
  bootImage: (id: string) => ['boot-images', id] as const,
  systemMetrics: ['system-metrics'] as const,
  computerMetrics: (id: string) => ['computer-metrics', id] as const,
  users: ['users'] as const,
  user: (id: string) => ['users', id] as const,
  games: ['games'] as const,
  game: (id: string) => ['games', id] as const,
  networkConfig: ['network-config'] as const,
  licenses: ['licenses'] as const,
  license: (id: string) => ['licenses', id] as const,
  health: ['health'] as const,
};

// ==================== Computer Hooks ====================

export function useComputers() {
  return useQuery({
    queryKey: queryKeys.computers,
    queryFn: () => ggRockAPI.getComputers(),
    refetchInterval: 10000, // Refetch every 10 seconds
  });
}

export function useComputer(id: string) {
  return useQuery({
    queryKey: queryKeys.computer(id),
    queryFn: () => ggRockAPI.getComputer(id),
    enabled: !!id,
  });
}

export function useComputerAction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (action: ComputerAction) => ggRockAPI.executeComputerAction(action),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.computers });
    },
  });
}

export function useRebootComputer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (computerId: string) => ggRockAPI.rebootComputer(computerId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.computers });
    },
  });
}

export function useShutdownComputer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (computerId: string) => ggRockAPI.shutdownComputer(computerId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.computers });
    },
  });
}

export function useWakeupComputer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (computerId: string) => ggRockAPI.wakeupComputer(computerId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.computers });
    },
  });
}

// ==================== Session Hooks ====================

export function useActiveSessions() {
  return useQuery({
    queryKey: queryKeys.activeSessions,
    queryFn: () => ggRockAPI.getActiveSessions(),
    refetchInterval: 5000, // Refetch every 5 seconds
  });
}

export function useSessions() {
  return useQuery({
    queryKey: queryKeys.sessions,
    queryFn: () => ggRockAPI.getAllSessions(),
  });
}

export function useSession(id: string) {
  return useQuery({
    queryKey: queryKeys.session(id),
    queryFn: () => ggRockAPI.getSession(id),
    enabled: !!id,
  });
}

export function useEndSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sessionId: string) => ggRockAPI.endSession(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.sessions });
      queryClient.invalidateQueries({ queryKey: queryKeys.activeSessions });
    },
  });
}

// ==================== Boot Image Hooks ====================

export function useBootImages() {
  return useQuery({
    queryKey: queryKeys.bootImages,
    queryFn: () => ggRockAPI.getBootImages(),
  });
}

export function useBootImage(id: string) {
  return useQuery({
    queryKey: queryKeys.bootImage(id),
    queryFn: () => ggRockAPI.getBootImage(id),
    enabled: !!id,
  });
}

export function useDeployBootImage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (deployment: DeploymentRequest) => ggRockAPI.deployBootImage(deployment),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.computers });
      queryClient.invalidateQueries({ queryKey: queryKeys.bootImages });
    },
  });
}

// ==================== System Metrics Hooks ====================

export function useSystemMetrics() {
  return useQuery({
    queryKey: queryKeys.systemMetrics,
    queryFn: () => ggRockAPI.getSystemMetrics(),
    refetchInterval: 5000, // Refetch every 5 seconds
  });
}

export function useComputerMetrics(computerId: string) {
  return useQuery({
    queryKey: queryKeys.computerMetrics(computerId),
    queryFn: () => ggRockAPI.getComputerMetrics(computerId),
    enabled: !!computerId,
    refetchInterval: 5000,
  });
}

// ==================== User Hooks ====================

export function useUsers() {
  return useQuery({
    queryKey: queryKeys.users,
    queryFn: () => ggRockAPI.getUsers(),
  });
}

export function useUser(id: string) {
  return useQuery({
    queryKey: queryKeys.user(id),
    queryFn: () => ggRockAPI.getUser(id),
    enabled: !!id,
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userData: Partial<GGRockUser>) => ggRockAPI.createUser(userData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users });
    },
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<GGRockUser> }) => 
      ggRockAPI.updateUser(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users });
      queryClient.invalidateQueries({ queryKey: queryKeys.user(variables.id) });
    },
  });
}

export function useDeleteUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => ggRockAPI.deleteUser(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users });
    },
  });
}

// ==================== Game Library Hooks ====================

export function useGames() {
  return useQuery({
    queryKey: queryKeys.games,
    queryFn: () => ggRockAPI.getGames(),
  });
}

export function useGame(id: string) {
  return useQuery({
    queryKey: queryKeys.game(id),
    queryFn: () => ggRockAPI.getGame(id),
    enabled: !!id,
  });
}

// ==================== Network Config Hooks ====================

export function useNetworkConfig() {
  return useQuery({
    queryKey: queryKeys.networkConfig,
    queryFn: () => ggRockAPI.getNetworkConfig(),
  });
}

export function useUpdateNetworkConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (config: Partial<NetworkConfig>) => ggRockAPI.updateNetworkConfig(config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.networkConfig });
    },
  });
}

// ==================== License Hooks ====================

export function useLicenses() {
  return useQuery({
    queryKey: queryKeys.licenses,
    queryFn: () => ggRockAPI.getLicenses(),
  });
}

export function useLicense(id: string) {
  return useQuery({
    queryKey: queryKeys.license(id),
    queryFn: () => ggRockAPI.getLicense(id),
    enabled: !!id,
  });
}

// ==================== Health Check Hooks ====================

export function useHealth() {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: () => ggRockAPI.checkHealth(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

// ==================== Authentication Hook ====================

export function useAuth() {
  const queryClient = useQueryClient();

  const login = useMutation({
    mutationFn: (credentials: AuthCredentials) => ggRockAPI.authenticate(credentials),
  });

  const logout = useMutation({
    mutationFn: () => ggRockAPI.logout(),
    onSuccess: () => {
      queryClient.clear();
    },
  });

  return {
    login,
    logout,
    isAuthenticated: ggRockAPI.isAuthenticated(),
    currentUser: ggRockAPI.getCurrentUser(),
  };
}

