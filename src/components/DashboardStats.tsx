import { Monitor, Users, Activity, HardDrive } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useSystemMetrics } from '@/hooks/useGGRockAPI';
import { useSystemMetricsUpdates } from '@/hooks/useGGRockWebSocket';
import { formatBytes } from '@/lib/utils';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  description?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
}

function StatCard({ title, value, icon, description, trend }: StatCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {description && (
          <p className="text-xs text-muted-foreground mt-1">{description}</p>
        )}
        {trend && (
          <p className={`text-xs mt-1 ${trend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
            {trend.isPositive ? '+' : ''}{trend.value}% from last hour
          </p>
        )}
      </CardContent>
    </Card>
  );
}

export default function DashboardStats() {
  const { data: metrics, isLoading } = useSystemMetrics();
  const { data: realtimeMetrics, isConnected } = useSystemMetricsUpdates();

  // Use realtime data if available, otherwise fall back to polled data
  const currentMetrics = realtimeMetrics || metrics;

  if (isLoading || !currentMetrics) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="space-y-0 pb-2">
              <div className="h-4 bg-gray-200 rounded w-24" />
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-gray-200 rounded w-16" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {isConnected && (
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span>Live updates enabled</span>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Computers"
          value={currentMetrics.totalComputers}
          icon={<Monitor className="h-4 w-4 text-muted-foreground" />}
          description={`${currentMetrics.onlineComputers} online, ${currentMetrics.offlineComputers} offline`}
        />

        <StatCard
          title="Active Sessions"
          value={currentMetrics.activeSessions}
          icon={<Users className="h-4 w-4 text-muted-foreground" />}
          description="Currently playing"
        />

        <StatCard
          title="Avg CPU Usage"
          value={`${currentMetrics.cpuUsageAverage.toFixed(1)}%`}
          icon={<Activity className="h-4 w-4 text-muted-foreground" />}
          description={`Memory: ${currentMetrics.memoryUsageAverage.toFixed(1)}%`}
        />

        <StatCard
          title="Disk Usage"
          value={`${currentMetrics.diskUsage.percentage.toFixed(1)}%`}
          icon={<HardDrive className="h-4 w-4 text-muted-foreground" />}
          description={`${formatBytes(currentMetrics.diskUsage.free)} free`}
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">System Status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Online Computers</span>
              <div className="flex items-center gap-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full"
                    style={{ 
                      width: `${(currentMetrics.onlineComputers / currentMetrics.totalComputers) * 100}%` 
                    }}
                  />
                </div>
                <span className="text-sm font-medium w-12 text-right">
                  {Math.round((currentMetrics.onlineComputers / currentMetrics.totalComputers) * 100)}%
                </span>
              </div>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Average CPU</span>
              <div className="flex items-center gap-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ width: `${currentMetrics.cpuUsageAverage}%` }}
                  />
                </div>
                <span className="text-sm font-medium w-12 text-right">
                  {currentMetrics.cpuUsageAverage.toFixed(1)}%
                </span>
              </div>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Average Memory</span>
              <div className="flex items-center gap-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-purple-500 h-2 rounded-full"
                    style={{ width: `${currentMetrics.memoryUsageAverage}%` }}
                  />
                </div>
                <span className="text-sm font-medium w-12 text-right">
                  {currentMetrics.memoryUsageAverage.toFixed(1)}%
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Network Traffic</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Incoming</span>
              <span className="text-sm font-medium">
                {formatBytes(currentMetrics.networkTraffic.incoming)}/s
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Outgoing</span>
              <span className="text-sm font-medium">
                {formatBytes(currentMetrics.networkTraffic.outgoing)}/s
              </span>
            </div>

            <div className="pt-3 border-t">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Total Storage</span>
                <span className="text-sm font-medium">
                  {formatBytes(currentMetrics.diskUsage.total)}
                </span>
              </div>
              <div className="flex justify-between items-center mt-2">
                <span className="text-sm text-muted-foreground">Used</span>
                <span className="text-sm font-medium">
                  {formatBytes(currentMetrics.diskUsage.used)}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

