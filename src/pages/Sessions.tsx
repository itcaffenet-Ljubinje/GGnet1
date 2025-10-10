import SessionManager from '@/components/SessionManager';

export default function Sessions() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Session Management</h1>
        <p className="text-muted-foreground">
          Monitor and manage user gaming sessions
        </p>
      </div>

      <SessionManager />
    </div>
  );
}

