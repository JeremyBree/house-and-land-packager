import { Link } from 'react-router-dom'
import { Building2, Users, MapPin, Briefcase } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { PageHeader } from '@/components/common/PageHeader'
import { useAuth } from '@/hooks/useAuth'

export default function DashboardPage() {
  const { user, hasRole } = useAuth()
  const isAdmin = hasRole('admin')

  return (
    <div>
      <PageHeader
        title={`Welcome, ${user?.first_name ?? ''}`}
        description="House & Land Packager — Sprint 1"
      />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Your account</CardTitle>
            <CardDescription>{user?.email}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {user?.roles.map((r) => (
                <span key={r} className="rounded-full bg-secondary px-2 py-0.5 text-xs font-medium">
                  {r}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>

        <Link to="/estates" className="group">
          <Card className="h-full transition-colors group-hover:border-primary">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-base">Estates</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Browse estates and developers.</p>
            </CardContent>
          </Card>
        </Link>

        {isAdmin && (
          <>
            <Link to="/admin/users" className="group">
              <Card className="h-full transition-colors group-hover:border-primary">
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle className="text-base">Users</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">Manage users and roles.</p>
                </CardContent>
              </Card>
            </Link>
            <Link to="/admin/regions" className="group">
              <Card className="h-full transition-colors group-hover:border-primary">
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle className="text-base">Regions</CardTitle>
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">Region master data.</p>
                </CardContent>
              </Card>
            </Link>
            <Link to="/admin/developers" className="group">
              <Card className="h-full transition-colors group-hover:border-primary">
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle className="text-base">Developers</CardTitle>
                  <Briefcase className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">Developer master data.</p>
                </CardContent>
              </Card>
            </Link>
          </>
        )}
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="text-base">Sprint 1 status</CardTitle>
          <CardDescription>Authentication and estate management are online.</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="list-inside list-disc space-y-1 text-sm text-muted-foreground">
            <li>JWT authentication with role-based access</li>
            <li>Estates, Regions, Developers CRUD</li>
            <li>User management (admin)</li>
            <li>Packages, Pricing Requests, Land Search coming in Sprint 2</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}
