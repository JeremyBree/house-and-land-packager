import { NavLink } from 'react-router-dom'
import {
  AlertTriangle,
  Building2,
  Calculator,
  ClipboardList,
  DollarSign,
  FileText,
  FileUp,
  Globe,
  Home,
  LayoutDashboard,
  Zap,
  MapPin,
  Package,
  Search,
  ShieldCheck,
  SlidersHorizontal,
  Users,
  Briefcase,
  HandCoins,
  KeyRound,
  Truck,
  Mountain,
  MapPinned,
  TrendingUp,
  BookOpen,
  Tags,
  ListPlus,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuth } from '@/hooks/useAuth'

interface NavItem {
  to: string
  label: string
  icon: React.ComponentType<{ className?: string }>
  disabled?: boolean
  tooltip?: string
}

const mainNav: NavItem[] = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/estates', label: 'Estates', icon: Building2 },
  { to: '/packages', label: 'Packages', icon: Package },
  { to: '/conflicts', label: 'Conflicts', icon: AlertTriangle },
  { to: '/pricing-requests', label: 'Pricing Requests', icon: FileText },
  { to: '/lsi', label: 'Land Search', icon: Search },
  { to: '/pdf-ingestion', label: 'PDF Ingestion', icon: FileUp },
]

const adminNav: NavItem[] = [
  { to: '/admin/users', label: 'Users', icon: Users },
  { to: '/admin/regions', label: 'Regions', icon: MapPin },
  { to: '/admin/developers', label: 'Developers', icon: Briefcase },
  { to: '/admin/house-designs', label: 'House Designs', icon: Home },
  { to: '/admin/energy-ratings', label: 'Energy Ratings', icon: Zap },
  { to: '/admin/commissions', label: 'Commissions', icon: HandCoins },
  { to: '/admin/pricing-templates', label: 'Pricing Templates', icon: SlidersHorizontal },
  { to: '/admin/pricing-rules', label: 'Pricing Rules', icon: Calculator },
  { to: '/admin/pricing-config', label: 'Pricing Config', icon: DollarSign },
  { to: '/admin/travel-surcharges', label: 'Travel Surcharges', icon: Truck },
  { to: '/admin/site-costs', label: 'Site Costs', icon: Mountain },
  { to: '/admin/postcode-costs', label: 'Postcode Costs', icon: MapPinned },
  { to: '/admin/fbc-bands', label: 'FBC Bands', icon: TrendingUp },
  { to: '/admin/upgrades', label: 'Upgrades', icon: ListPlus },
  { to: '/admin/guideline-categories', label: 'Guideline Categories', icon: Tags },
  { to: '/admin/estate-guidelines', label: 'Estate Guidelines', icon: BookOpen },
  { to: '/admin/api-keys', label: 'API Keys', icon: KeyRound },
  { to: '/admin/configurations', label: 'Configurations', icon: Globe },
  { to: '/admin/ingestion-logs', label: 'Ingestion Logs', icon: ClipboardList },
]

export function Sidebar() {
  const { user, hasRole } = useAuth()
  const isAdmin = hasRole('admin')

  return (
    <aside className="flex h-full w-60 shrink-0 flex-col bg-sidebar text-sidebar-foreground">
      <div className="flex h-16 items-center border-b border-white/10 px-6">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-white/10">
            <Building2 className="h-5 w-5" />
          </div>
          <div>
            <div className="text-sm font-semibold leading-tight">HBG Packager</div>
            <div className="text-[10px] uppercase tracking-wider opacity-60">House &amp; Land</div>
          </div>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-4">
        <div className="mb-1 px-3 text-[10px] font-semibold uppercase tracking-wider text-white/40">Main</div>
        <ul className="space-y-1">
          {mainNav.map((item) => (
            <li key={item.to}>
              {item.disabled ? (
                <div
                  title={item.tooltip}
                  className="flex cursor-not-allowed items-center gap-3 rounded-md px-3 py-2 text-sm opacity-40"
                >
                  <item.icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </div>
              ) : (
                <NavLink
                  to={item.to}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors',
                      isActive
                        ? 'bg-sidebar-accent text-sidebar-accent-foreground font-medium'
                        : 'text-white/80 hover:bg-white/5 hover:text-white',
                    )
                  }
                >
                  <item.icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </NavLink>
              )}
            </li>
          ))}
        </ul>

        {isAdmin && (
          <>
            <div className="mb-1 mt-6 flex items-center gap-2 px-3 text-[10px] font-semibold uppercase tracking-wider text-white/40">
              <ShieldCheck className="h-3 w-3" />
              Admin
            </div>
            <ul className="space-y-1">
              {adminNav.map((item) => (
                <li key={item.to}>
                  <NavLink
                    to={item.to}
                    className={({ isActive }) =>
                      cn(
                        'flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors',
                        isActive
                          ? 'bg-sidebar-accent text-sidebar-accent-foreground font-medium'
                          : 'text-white/80 hover:bg-white/5 hover:text-white',
                      )
                    }
                  >
                    <item.icon className="h-4 w-4" />
                    <span>{item.label}</span>
                  </NavLink>
                </li>
              ))}
            </ul>
          </>
        )}
      </nav>

      {user && (
        <div className="border-t border-white/10 p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/10 text-xs font-semibold">
              {user.first_name.charAt(0)}
              {user.last_name.charAt(0)}
            </div>
            <div className="min-w-0 flex-1">
              <div className="truncate text-sm font-medium">
                {user.first_name} {user.last_name}
              </div>
              <div className="truncate text-xs opacity-60">{user.email}</div>
            </div>
          </div>
        </div>
      )}
    </aside>
  )
}
