import { HardDrive, Upload, Download, Trash2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useBootImages, useDeployBootImage } from '@/hooks/useGGRockAPI';
import { formatBytes } from '@/lib/utils';

export default function BootImages() {
  const { data: bootImages, isLoading } = useBootImages();
  const deployMutation = useDeployBootImage();

  const handleDeploy = async (imageId: string) => {
    // In a real implementation, you would show a dialog to select computers
    const confirmation = confirm('Deploy this boot image to selected computers?');
    if (confirmation) {
      try {
        await deployMutation.mutateAsync({
          imageId,
          computerIds: [], // Would be selected from a dialog
          forceReboot: false,
        });
      } catch (error) {
        console.error('Deployment failed:', error);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center space-y-2">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto" />
          <p className="text-sm text-muted-foreground">Loading boot images...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Boot Images</h1>
          <p className="text-muted-foreground">
            Manage diskless boot images and deployments
          </p>
        </div>
        <Button>
          <Upload className="h-4 w-4 mr-2" />
          Upload Image
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {bootImages?.map((image) => (
          <Card key={image.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <HardDrive className="h-5 w-5 text-primary" />
                  <CardTitle className="text-lg">{image.name}</CardTitle>
                </div>
                {image.isDefault && (
                  <Badge variant="default">Default</Badge>
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {image.description && (
                <p className="text-sm text-muted-foreground">{image.description}</p>
              )}

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Type</span>
                  <Badge variant="outline">{image.type}</Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Version</span>
                  <span className="font-medium">{image.version}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Size</span>
                  <span className="font-medium">{formatBytes(image.size)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Updated</span>
                  <span className="font-medium">
                    {new Date(image.updatedAt).toLocaleDateString()}
                  </span>
                </div>
              </div>

              {image.installedGames && image.installedGames.length > 0 && (
                <div className="pt-3 border-t">
                  <p className="text-xs text-muted-foreground mb-2">
                    {image.installedGames.length} games installed
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {image.installedGames.slice(0, 3).map((game, idx) => (
                      <Badge key={idx} variant="secondary" className="text-xs">
                        {game}
                      </Badge>
                    ))}
                    {image.installedGames.length > 3 && (
                      <Badge variant="secondary" className="text-xs">
                        +{image.installedGames.length - 3} more
                      </Badge>
                    )}
                  </div>
                </div>
              )}

              <div className="flex gap-2 pt-2">
                <Button
                  size="sm"
                  className="flex-1"
                  onClick={() => handleDeploy(image.id)}
                  disabled={deployMutation.isPending}
                >
                  <Download className="h-4 w-4 mr-1" />
                  Deploy
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                >
                  Edit
                </Button>
                <Button
                  size="sm"
                  variant="destructive"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {!bootImages?.length && (
        <div className="text-center py-12">
          <HardDrive className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-sm text-muted-foreground">No boot images found</p>
        </div>
      )}
    </div>
  );
}

