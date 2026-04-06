import { useLocation, useNavigate } from 'react-router-dom'
import { LogOut, User as UserIcon } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/hooks/useAuth'
import { NotificationBell } from '@/components/notifications/NotificationBell'

const TITLES: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/estates': 'Estates',
  '/packages': 'Packages',
  '/pricing-requests': 'Pricing Requests',
  '/pricing-requests/new': 'New Pricing Request',
  '/notifications': 'Notifications',
  '/lsi': 'Land Search',
  '/admin/users': 'Users',
  '/admin/regions': 'Regions',
  '/admin/developers': 'Developers',
}

function getTitle(path: string): string {
  if (TITLES[path]) return TITLES[path]
  if (path.startsWith('/estates/')) return 'Estate Details'
  if (path.startsWith('/pricing-requests/')) return 'Pricing Request Details'
  return 'HBG Packager'
}

export function Header() {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b bg-background px-6">
      <h1 className="text-lg font-semibold">{getTitle(location.pathname)}</h1>
      <div className="flex items-center gap-2">
      <NotificationBell />
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="sm" className="gap-2">
            <UserIcon className="h-4 w-4" />
            <span className="text-sm">{user?.first_name} {user?.last_name}</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuLabel>
            <div className="flex flex-col">
              <span className="text-sm font-medium">
                {user?.first_name} {user?.last_name}
              </span>
              <span className="text-xs font-normal text-muted-foreground">{user?.email}</span>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={handleLogout} className="gap-2 text-destructive focus:text-destructive">
            <LogOut className="h-4 w-4" />
            Log out
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
      </div>
    </header>
  )
}
