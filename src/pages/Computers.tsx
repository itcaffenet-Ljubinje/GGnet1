import ComputerGrid from '@/components/ComputerGrid';

export default function Computers() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Computer Management</h1>
        <p className="text-muted-foreground">
          Monitor and control all computers in your gaming center
        </p>
      </div>

      <ComputerGrid />
    </div>
  );
}

