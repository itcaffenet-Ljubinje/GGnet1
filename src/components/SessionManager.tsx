import { Users, Clock, Monitor, XCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useActiveSessions, useEndSession } from '@/hooks/useGGRockAPI';
import { useSessionUpdates } from '@/hooks/useGGRockWebSocket';
import { getStatusColor, formatDuration } from '@/lib/utils';
import type { GGRockSession } from '@/types/ggrock';

interface SessionCardProps {
  session: GGRockSession;
  onEndSession: (sessionId: string) => void;
}

function SessionCard({ session, onEndSession }: SessionCardProps) {
  const statusColor = getStatusColor(session.status);

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-3 flex-1">
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-primary" />
              <h3 className="font-semibold text-lg">{session.username}</h3>
              <Badge className={statusColor}>{session.status}</Badge>
            </div>

            <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Monitor className="h-4 w-4" />
                <span>{session.computerName}</span>
              </div>
              <div className="flex items-center gap-2 text-muted-foreground">
                <Clock className="h-4 w-4" />
                <span>{formatDuration(session.duration)}</span>
              </div>
              {session.currentGame && (
                <div className="col-span-2 text-sm">
                  <span className="text-muted-foreground">Playing: </span>
                  <span className="font-medium">{session.currentGame}</span>
                </div>
              )}
              {session.ipAddress && (
                <div className="col-span-2 text-xs text-muted-foreground">
                  IP: {session.ipAddress}
                </div>
              )}
            </div>

            <div className="text-xs text-muted-foreground">
              Started: {new Date(session.startTime).toLocaleString()}
            </div>
          </div>

          {session.status === 'active' && (
            <Button
              size="sm"
              variant="destructive"
              onClick={() => onEndSession(session.id)}
            >
              <XCircle className="h-4 w-4 mr-1" />
              End
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default function SessionManager() {
  const { data: sessions, isLoading, error } = useActiveSessions();
  const { data: realtimeUpdates, isConnected } = useSessionUpdates();
  const endSessionMutation = useEndSession();

  const handleEndSession = async (sessionId: string) => {
    if (confirm('Are you sure you want to end this session?')) {
      await endSessionMutation.mutateAsync(sessionId);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center space-y-2">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto" />
          <p className="text-sm text-muted-foreground">Loading sessions...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center space-y-2">
          <XCircle className="h-12 w-12 text-destructive mx-auto" />
          <p className="text-sm font-medium">Failed to load sessions</p>
          <p className="text-xs text-muted-foreground">Please check your connection</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Active Sessions</h2>
          <p className="text-sm text-muted-foreground">
            {sessions?.length || 0} active sessions {isConnected && '• Live updates'}
          </p>
        </div>
      </div>

      <div className="grid gap-4">
        {sessions?.map((session) => (
          <SessionCard
            key={session.id}
            session={session}
            onEndSession={handleEndSession}
          />
        ))}
      </div>

      {!sessions?.length && (
        <div className="text-center py-12">
          <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-sm text-muted-foreground">No active sessions</p>
        </div>
      )}
    </div>
  );
}

