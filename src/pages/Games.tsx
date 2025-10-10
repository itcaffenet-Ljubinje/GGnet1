import { Gamepad2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useGames } from '@/hooks/useGGRockAPI';
import { formatBytes } from '@/lib/utils';

export default function Games() {
  const { data: games, isLoading } = useGames();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center space-y-2">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto" />
          <p className="text-sm text-muted-foreground">Loading games...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Game Library</h1>
        <p className="text-muted-foreground">
          Manage games available across boot images
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {games?.map((game) => (
          <Card key={game.id}>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Gamepad2 className="h-5 w-5 text-primary" />
                <CardTitle className="text-lg truncate">{game.name}</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {game.publisher && (
                <p className="text-sm text-muted-foreground">{game.publisher}</p>
              )}

              <div className="space-y-2 text-sm">
                {game.version && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Version</span>
                    <span className="font-medium">{game.version}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Size</span>
                  <span className="font-medium">{formatBytes(game.size)}</span>
                </div>
              </div>

              {game.bootImages && game.bootImages.length > 0 && (
                <div className="pt-3 border-t">
                  <p className="text-xs text-muted-foreground mb-2">
                    Available on {game.bootImages.length} boot image{game.bootImages.length !== 1 ? 's' : ''}
                  </p>
                  <Badge variant="secondary" className="text-xs">
                    {game.bootImages.length} image{game.bootImages.length !== 1 ? 's' : ''}
                  </Badge>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {!games?.length && (
        <div className="text-center py-12">
          <Gamepad2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-sm text-muted-foreground">No games found</p>
        </div>
      )}
    </div>
  );
}

