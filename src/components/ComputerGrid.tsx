import { Monitor, Power, PowerOff, WifiOff, Activity } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useComputers, useRebootComputer, useShutdownComputer, useWakeupComputer } from '@/hooks/useGGRockAPI';
import { useComputerStatusUpdates } from '@/hooks/useGGRockWebSocket';
import { getStatusColor, formatUptime } from '@/lib/utils';
import type { GGRockComputer } from '@/types/ggrock';

interface ComputerCardProps {
  computer: GGRockComputer;
  onRemoteAccess: (computerId: string) => void;
  onReboot: (computerId: string) => void;
  onShutdown: (computerId: string) => void;
  onWakeup: (computerId: string) => void;
}

function ComputerCard({ computer, onRemoteAccess, onReboot, onShutdown, onWakeup }: ComputerCardProps) {
  const statusColor = getStatusColor(computer.status);

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Monitor className="h-5 w-5 text-primary" />
            <CardTitle className="text-lg">{computer.hostname}</CardTitle>
          </div>
          <Badge className={statusColor}>{computer.status}</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="space-y-1">
            <p className="text-muted-foreground">IP Address</p>
            <p className="font-medium">{computer.ipAddress}</p>
          </div>
          <div className="space-y-1">
            <p className="text-muted-foreground">MAC Address</p>
            <p className="font-mono text-xs">{computer.macAddress}</p>
          </div>
          <div className="space-y-1">
            <p className="text-muted-foreground">Boot Image</p>
            <p className="font-medium truncate">{computer.bootImage}</p>
          </div>
          {computer.uptime && (
            <div className="space-y-1">
              <p className="text-muted-foreground">Uptime</p>
              <p className="font-medium">{formatUptime(computer.uptime)}</p>
            </div>
          )}
        </div>

        {computer.status === 'online' && computer.cpuUsage !== undefined && (
          <div className="space-y-2 pt-2 border-t">
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">CPU</span>
              <span className="font-medium">{computer.cpuUsage}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary h-2 rounded-full transition-all"
                style={{ width: `${computer.cpuUsage}%` }}
              />
            </div>
            {computer.memoryUsage !== undefined && (
              <>
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground">Memory</span>
                  <span className="font-medium">{computer.memoryUsage}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all"
                    style={{ width: `${computer.memoryUsage}%` }}
                  />
                </div>
              </>
            )}
          </div>
        )}

        <div className="flex gap-2 pt-2">
          {computer.status === 'online' && (
            <>
              <Button
                size="sm"
                variant="outline"
                className="flex-1"
                onClick={() => onRemoteAccess(computer.id)}
              >
                <Activity className="h-4 w-4 mr-1" />
                VNC
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => onReboot(computer.id)}
              >
                <Power className="h-4 w-4" />
              </Button>
              <Button
                size="sm"
                variant="destructive"
                onClick={() => onShutdown(computer.id)}
              >
                <PowerOff className="h-4 w-4" />
              </Button>
            </>
          )}
          {computer.status === 'offline' && (
            <Button
              size="sm"
              variant="default"
              className="flex-1"
              onClick={() => onWakeup(computer.id)}
            >
              <Power className="h-4 w-4 mr-1" />
              Wake Up
            </Button>
          )}
          {computer.status === 'booting' && (
            <Button size="sm" variant="outline" className="flex-1" disabled>
              Booting...
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default function ComputerGrid() {
  const { data: computers, isLoading, error } = useComputers();
  const { data: realtimeUpdates, isConnected } = useComputerStatusUpdates();
  
  const rebootMutation = useRebootComputer();
  const shutdownMutation = useShutdownComputer();
  const wakeupMutation = useWakeupComputer();

  const handleRemoteAccess = (computerId: string) => {
    const vncUrl = `${import.meta.env.VITE_GGROCK_VNC_URL || 'http://localhost:6080'}/vnc/?host=${computerId}`;
    window.open(vncUrl, '_blank', 'width=1280,height=720');
  };

  const handleReboot = async (computerId: string) => {
    if (confirm('Are you sure you want to reboot this computer?')) {
      await rebootMutation.mutateAsync(computerId);
    }
  };

  const handleShutdown = async (computerId: string) => {
    if (confirm('Are you sure you want to shutdown this computer?')) {
      await shutdownMutation.mutateAsync(computerId);
    }
  };

  const handleWakeup = async (computerId: string) => {
    await wakeupMutation.mutateAsync(computerId);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center space-y-2">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto" />
          <p className="text-sm text-muted-foreground">Loading computers...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center space-y-2">
          <WifiOff className="h-12 w-12 text-destructive mx-auto" />
          <p className="text-sm font-medium">Failed to load computers</p>
          <p className="text-xs text-muted-foreground">Please check your connection</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Computers</h2>
          <p className="text-sm text-muted-foreground">
            {computers?.length || 0} total computers {isConnected && '• Live updates'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {computers?.map((computer) => (
          <ComputerCard
            key={computer.id}
            computer={computer}
            onRemoteAccess={handleRemoteAccess}
            onReboot={handleReboot}
            onShutdown={handleShutdown}
            onWakeup={handleWakeup}
          />
        ))}
      </div>

      {!computers?.length && (
        <div className="text-center py-12">
          <Monitor className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-sm text-muted-foreground">No computers found</p>
        </div>
      )}
    </div>
  );
}

