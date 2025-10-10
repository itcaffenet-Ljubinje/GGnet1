import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Monitor, 
  Users as UsersIcon, 
  HardDrive, 
  Gamepad2, 
  Network, 
  Settings, 
  LogOut,
  Menu,
  X
} from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useGGRockAPI';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Computers', href: '/computers', icon: Monitor },
  { name: 'Sessions', href: '/sessions', icon: UsersIcon },
  { name: 'Boot Images', href: '/boot-images', icon: HardDrive },
  { name: 'Games', href: '/games', icon: Gamepad2 },
  { name: 'Network', href: '/network', icon: Network },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const location = useLocation();
  const navigate = useNavigate();
  const { currentUser, logout } = useAuth();

  const handleLogout = async () => {
    await logout.mutateAsync();
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside
        className={cn(
          'bg-card border-r border-border transition-all duration-300 flex flex-col',
          sidebarOpen ? 'w-64' : 'w-20'
        )}
      >
        {/* Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-border">
          {sidebarOpen && (
            <h1 className="text-xl font-bold text-primary">GGRock</h1>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                )}
                title={!sidebarOpen ? item.name : undefined}
              >
                <item.icon className="h-5 w-5 flex-shrink-0" />
                {sidebarOpen && <span>{item.name}</span>}
              </Link>
            );
          })}
        </nav>

        {/* User section */}
        <div className="p-4 border-t border-border">
          {sidebarOpen ? (
            <div className="space-y-3">
              {currentUser && (
                <div className="px-3 py-2">
                  <p className="text-sm font-medium">{currentUser.username}</p>
                  <p className="text-xs text-muted-foreground">{currentUser.role}</p>
                </div>
              )}
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={handleLogout}
              >
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          ) : (
            <Button
              variant="outline"
              size="icon"
              onClick={handleLogout}
              title="Logout"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="h-16 border-b border-border flex items-center justify-between px-6">
          <div>
            <h2 className="text-lg font-semibold">
              {navigation.find((item) => item.href === location.pathname)?.name || 'Dashboard'}
            </h2>
          </div>
          {currentUser && (
            <div className="flex items-center gap-4">
              <div className="text-sm text-muted-foreground">
                Welcome, <span className="font-medium text-foreground">{currentUser.username}</span>
              </div>
            </div>
          )}
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

