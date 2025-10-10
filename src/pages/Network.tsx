import { Network as NetworkIcon, Wifi } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useNetworkConfig } from '@/hooks/useGGRockAPI';

export default function Network() {
  const { data: config, isLoading } = useNetworkConfig();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center space-y-2">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto" />
          <p className="text-sm text-muted-foreground">Loading network configuration...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Network Configuration</h1>
        <p className="text-muted-foreground">
          Configure network settings for your gaming center
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <NetworkIcon className="h-5 w-5" />
              DHCP Settings
            </CardTitle>
            <CardDescription>
              Configure DHCP server for client computers
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>DHCP Enabled</Label>
              <div className="flex items-center gap-2">
                <Badge variant={config?.dhcpEnabled ? 'default' : 'secondary'}>
                  {config?.dhcpEnabled ? 'Enabled' : 'Disabled'}
                </Badge>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="ip-start">IP Range Start</Label>
              <Input
                id="ip-start"
                defaultValue={config?.ipRange.start}
                placeholder="192.168.1.100"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="ip-end">IP Range End</Label>
              <Input
                id="ip-end"
                defaultValue={config?.ipRange.end}
                placeholder="192.168.1.200"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="subnet">Subnet Mask</Label>
              <Input
                id="subnet"
                defaultValue={config?.subnet}
                placeholder="255.255.255.0"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="gateway">Gateway</Label>
              <Input
                id="gateway"
                defaultValue={config?.gateway}
                placeholder="192.168.1.1"
              />
            </div>

            <Button className="w-full">Save DHCP Settings</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Wifi className="h-5 w-5" />
              DNS Configuration
            </CardTitle>
            <CardDescription>
              Configure DNS servers for name resolution
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="dns-primary">Primary DNS</Label>
              <Input
                id="dns-primary"
                defaultValue={config?.dns[0]}
                placeholder="8.8.8.8"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="dns-secondary">Secondary DNS</Label>
              <Input
                id="dns-secondary"
                defaultValue={config?.dns[1]}
                placeholder="8.8.4.4"
              />
            </div>

            {config?.vlanId && (
              <div className="space-y-2">
                <Label htmlFor="vlan">VLAN ID</Label>
                <Input
                  id="vlan"
                  type="number"
                  defaultValue={config.vlanId}
                  placeholder="100"
                />
              </div>
            )}

            <Button className="w-full">Save DNS Settings</Button>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>PXE Boot Configuration</CardTitle>
            <CardDescription>
              Network boot settings for diskless clients
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">TFTP Server</p>
                  <p className="font-medium">Active on port 69</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Boot Files</p>
                  <p className="font-medium">/opt/ggrock/boot_files/</p>
                </div>
                <div>
                  <p className="text-muted-foreground">iSCSI Target</p>
                  <p className="font-medium">Active on port 3260</p>
                </div>
                <div>
                  <p className="text-muted-foreground">NFS Shares</p>
                  <p className="font-medium">Configured</p>
                </div>
              </div>
              
              <Button variant="outline" className="w-full">
                Advanced PXE Settings
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function Badge({ variant, children }: { variant?: 'default' | 'secondary'; children: React.ReactNode }) {
  const className = variant === 'secondary' 
    ? 'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-secondary text-secondary-foreground'
    : 'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-primary text-primary-foreground';
  
  return <div className={className}>{children}</div>;
}

