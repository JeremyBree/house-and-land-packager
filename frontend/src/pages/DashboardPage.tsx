import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  AlertTriangle,
  Building2,
  FileText,
  Layers,
  Package,
  Plus,
  Search,
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { PageHeader } from '@/components/common/PageHeader'
import { useAuth } from '@/hooks/useAuth'
import { getDashboard } from '@/api/dashboard'

const statusColors: Record<string, string> = {
  Pending: 'bg-yellow-100 text-yellow-800',
  'In Progress': 'bg-blue-100 text-blue-800',
  Completed: 'bg-green-100 text-green-800',
}

const lotStatusColors: Record<string, string> = {
  Available: 'bg-green-500',
  Hold: 'bg-yellow-500',
  'Deposit Taken': 'bg-blue-500',
  Sold: 'bg-purple-500',
  Unavailable: 'bg-gray-400',
}

export default function DashboardPage() {
  const { user } = useAuth()

  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboard,
  })

  const totalLots = dashboard?.total_lots ?? 0

  return (
    <div>
      <PageHeader
        title={`Welcome, ${user?.first_name ?? ''}`}
        description="House & Land Packager Dashboard"
      />

      {/* Metric Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Link to="/estates" className="group">
          <Card className="h-full transition-colors group-hover:border-primary">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Estates
              </CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {isLoading ? '...' : dashboard?.total_estates ?? 0}
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link to="/lsi" className="group">
          <Card className="h-full transition-colors group-hover:border-primary">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Lots
              </CardTitle>
              <Layers className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {isLoading ? '...' : dashboard?.total_lots ?? 0}
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link to="/conflicts" className="group">
          <Card className="h-full transition-colors group-hover:border-primary">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Active Conflicts
              </CardTitle>
              <AlertTriangle
                className={`h-4 w-4 ${
                  (dashboard?.active_conflicts ?? 0) > 0
                    ? 'text-red-500'
                    : 'text-muted-foreground'
                }`}
              />
            </CardHeader>
            <CardContent>
              <div
                className={`text-2xl font-bold ${
                  (dashboard?.active_conflicts ?? 0) > 0 ? 'text-red-600' : 'text-green-600'
                }`}
              >
                {isLoading ? '...' : dashboard?.active_conflicts ?? 0}
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link to="/pricing-requests" className="group">
          <Card className="h-full transition-colors group-hover:border-primary">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Pending Requests
              </CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {isLoading ? '...' : dashboard?.pending_requests ?? 0}
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Lot Status Breakdown + Quick Actions */}
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Lot Status Breakdown</CardTitle>
            <CardDescription>Distribution of lots by current status</CardDescription>
          </CardHeader>
          <CardContent>
            {dashboard?.lot_status_breakdown && totalLots > 0 ? (
              <div className="space-y-3">
                {Object.entries(dashboard.lot_status_breakdown).map(([status, count]) => {
                  const pct = Math.round((count / totalLots) * 100)
                  return (
                    <div key={status} className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <span>{status}</span>
                        <span className="text-muted-foreground">
                          {count} ({pct}%)
                        </span>
                      </div>
                      <div className="h-2 w-full rounded-full bg-secondary">
                        <div
                          className={`h-2 rounded-full ${lotStatusColors[status] ?? 'bg-gray-400'}`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                {isLoading ? 'Loading...' : 'No lot data available'}
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Quick Actions</CardTitle>
            <CardDescription>Common tasks at a glance</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <Button asChild variant="outline" className="justify-start">
              <Link to="/pricing-requests/new">
                <Plus className="mr-2 h-4 w-4" />
                New Pricing Request
              </Link>
            </Button>
            <Button asChild variant="outline" className="justify-start">
              <Link to="/lsi">
                <Search className="mr-2 h-4 w-4" />
                Search Lots
              </Link>
            </Button>
            <Button asChild variant="outline" className="justify-start">
              <Link to="/conflicts">
                <AlertTriangle className="mr-2 h-4 w-4" />
                View Conflicts
              </Link>
            </Button>
            <Button asChild variant="outline" className="justify-start">
              <Link to="/packages">
                <Package className="mr-2 h-4 w-4" />
                Browse Packages
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Recent Pricing Requests */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="text-base">Recent Pricing Requests</CardTitle>
          <CardDescription>Last 5 pricing submissions</CardDescription>
        </CardHeader>
        <CardContent>
          {dashboard?.recent_requests && dashboard.recent_requests.length > 0 ? (
            <div className="space-y-3">
              {dashboard.recent_requests.map((req) => (
                <Link
                  key={req.request_id}
                  to={`/pricing-requests/${req.request_id}`}
                  className="flex items-center justify-between rounded-md border p-3 transition-colors hover:bg-muted/50"
                >
                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-medium">
                      {req.estate_name ?? 'Estate'} — {req.stage_name ?? 'Stage'}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {req.brand} &middot; {req.lot_count} lot{req.lot_count !== 1 ? 's' : ''}
                    </div>
                  </div>
                  <Badge className={statusColors[req.status] ?? 'bg-gray-100 text-gray-800'}>
                    {req.status}
                  </Badge>
                </Link>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              {isLoading ? 'Loading...' : 'No pricing requests yet'}
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
