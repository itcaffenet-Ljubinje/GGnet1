import DashboardStats from '@/components/DashboardStats';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useComputers, useActiveSessions } from '@/hooks/useGGRockAPI';
import { Monitor, Users, AlertCircle, CheckCircle } from 'lucide-react';

export default function Dashboard() {
  const { data: computers } = useComputers();
  const { data: sessions } = useActiveSessions();

  const onlineComputers = computers?.filter(c => c.status === 'online').length || 0;
  const offlineComputers = computers?.filter(c => c.status === 'offline').length || 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Overview of your gaming center operations
        </p>
      </div>

      <DashboardStats />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Health</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">Healthy</div>
            <p className="text-xs text-muted-foreground mt-1">
              All services operational
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Online Rate</CardTitle>
            <Monitor className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {computers && computers.length > 0 
                ? Math.round((onlineComputers / computers.length) * 100) 
                : 0}%
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {onlineComputers} of {computers?.length || 0} computers
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Utilization</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {onlineComputers > 0 
                ? Math.round(((sessions?.length || 0) / onlineComputers) * 100)
                : 0}%
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {sessions?.length || 0} active of {onlineComputers} online
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {sessions?.slice(0, 5).map((session) => (
              <div key={session.id} className="flex items-center justify-between py-2 border-b last:border-0">
                <div className="flex items-center gap-3">
                  <Users className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="font-medium">{session.username}</p>
                    <p className="text-sm text-muted-foreground">{session.computerName}</p>
                  </div>
                </div>
                <div className="text-sm text-muted-foreground">
                  {session.currentGame || 'No game'}
                </div>
              </div>
            ))}
            {(!sessions || sessions.length === 0) && (
              <div className="text-center py-6 text-muted-foreground">
                No recent activity
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

