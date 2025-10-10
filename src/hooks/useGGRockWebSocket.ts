/**
 * WebSocket Hook for Real-time GGRock Updates
 * Provides real-time data synchronization with exponential backoff reconnection
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import type { WebSocketMessage } from '@/types/ggrock';

interface UseWebSocketOptions {
  enabled?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onMessage?: (data: any) => void;
  onError?: (error: Event) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

interface WebSocketState<T> {
  data: T | null;
  isConnected: boolean;
  error: Event | null;
  reconnectAttempts: number;
}

const WS_BASE_URL = import.meta.env.VITE_GGROCK_WS_URL || 'ws://localhost:5000';

export function useGGRockWebSocket<T = any>(
  endpoint: string,
  options: UseWebSocketOptions = {}
): WebSocketState<T> & { send: (data: any) => void; reconnect: () => void } {
  const {
    enabled = true,
    reconnectInterval = 1000,
    maxReconnectAttempts = 5,
    onMessage,
    onError,
    onConnect,
    onDisconnect,
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Event | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const shouldReconnectRef = useRef(true);

  const connect = useCallback(() => {
    if (!enabled) return;
    
    try {
      const wsUrl = `${WS_BASE_URL}/ws${endpoint}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log(`WebSocket connected: ${endpoint}`);
        setIsConnected(true);
        setError(null);
        setReconnectAttempts(0);
        onConnect?.();
      };

      ws.onclose = () => {
        console.log(`WebSocket disconnected: ${endpoint}`);
        setIsConnected(false);
        onDisconnect?.();

        // Attempt to reconnect with exponential backoff
        if (shouldReconnectRef.current && reconnectAttempts < maxReconnectAttempts) {
          const delay = reconnectInterval * Math.pow(2, reconnectAttempts);
          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttempts + 1}/${maxReconnectAttempts})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectAttempts((prev) => prev + 1);
            connect();
          }, delay);
        }
      };

      ws.onerror = (event) => {
        console.error(`WebSocket error: ${endpoint}`, event);
        setError(event);
        onError?.(event);
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage<T> = JSON.parse(event.data);
          setData(message.payload);
          onMessage?.(message.payload);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };
    } catch (err) {
      console.error('Failed to create WebSocket connection:', err);
    }
  }, [endpoint, enabled, reconnectAttempts, reconnectInterval, maxReconnectAttempts, onMessage, onError, onConnect, onDisconnect]);

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const send = useCallback((data: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected. Cannot send data.');
    }
  }, []);

  const reconnect = useCallback(() => {
    disconnect();
    shouldReconnectRef.current = true;
    setReconnectAttempts(0);
    connect();
  }, [connect, disconnect]);

  useEffect(() => {
    if (enabled) {
      shouldReconnectRef.current = true;
      connect();
    }

    return () => {
      disconnect();
    };
  }, [enabled, connect, disconnect]);

  return {
    data,
    isConnected,
    error,
    reconnectAttempts,
    send,
    reconnect,
  };
}

// Specialized hooks for common endpoints

export function useComputerStatusUpdates() {
  return useGGRockWebSocket('/computers/status');
}

export function useSessionUpdates() {
  return useGGRockWebSocket('/sessions/updates');
}

export function useSystemMetricsUpdates() {
  return useGGRockWebSocket('/metrics/system');
}

export function useComputerMetricsUpdates(computerId: string) {
  return useGGRockWebSocket(`/computers/${computerId}/metrics`, {
    enabled: !!computerId,
  });
}

