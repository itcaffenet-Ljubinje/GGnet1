import { Settings as SettingsIcon, Bell, Shield, Database } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useHealth } from '@/hooks/useGGRockAPI';
import { Badge } from '@/components/ui/badge';

export default function Settings() {
  const { data: health } = useHealth();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Configure system settings and preferences
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <SettingsIcon className="h-5 w-5" />
              System Health
            </CardTitle>
            <CardDescription>
              Current system status and diagnostics
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Overall Status</span>
              <Badge variant={health?.status === 'healthy' ? 'default' : 'destructive'}>
                {health?.status || 'Unknown'}
              </Badge>
            </div>

            {health?.services?.map((service) => (
              <div key={service.name} className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">{service.name}</span>
                <Badge variant={service.status === 'up' ? 'default' : 'destructive'}>
                  {service.status}
                </Badge>
              </div>
            ))}

            <Button variant="outline" className="w-full">
              Run Diagnostics
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5" />
              Notifications
            </CardTitle>
            <CardDescription>
              Configure system alerts and notifications
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm">Computer offline alerts</span>
                <Badge>Enabled</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Session timeout warnings</span>
                <Badge>Enabled</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Disk space alerts</span>
                <Badge>Enabled</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Update notifications</span>
                <Badge variant="secondary">Disabled</Badge>
              </div>
            </div>

            <Button variant="outline" className="w-full">
              Configure Alerts
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Security
            </CardTitle>
            <CardDescription>
              Security and authentication settings
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Two-Factor Auth</span>
                <span className="font-medium">Optional</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Session Timeout</span>
                <span className="font-medium">30 minutes</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Password Policy</span>
                <span className="font-medium">Strong</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">API Access</span>
                <span className="font-medium">Enabled</span>
              </div>
            </div>

            <Button variant="outline" className="w-full">
              Security Settings
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              Database
            </CardTitle>
            <CardDescription>
              Database backup and maintenance
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Last Backup</span>
                <span className="font-medium">2 hours ago</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Backup Schedule</span>
                <span className="font-medium">Daily at 3:00 AM</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Database Size</span>
                <span className="font-medium">245 MB</span>
              </div>
            </div>

            <div className="flex gap-2">
              <Button variant="outline" className="flex-1">
                Backup Now
              </Button>
              <Button variant="outline" className="flex-1">
                Restore
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>About GGRock</CardTitle>
            <CardDescription>
              System information and version details
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Version</p>
                <p className="font-medium">0.1.2200.2324-1</p>
              </div>
              <div>
                <p className="text-muted-foreground">Frontend</p>
                <p className="font-medium">React 18.2.0</p>
              </div>
              <div>
                <p className="text-muted-foreground">Backend</p>
                <p className="font-medium">.NET Core API</p>
              </div>
              <div>
                <p className="text-muted-foreground">Database</p>
                <p className="font-medium">PostgreSQL 12</p>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t">
              <p className="text-xs text-muted-foreground">
                © 2025 ggCircuit LLC. Enterprise-grade diskless boot system for esports centers.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

