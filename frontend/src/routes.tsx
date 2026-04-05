import { Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import LoginPage from '@/pages/LoginPage'
import DashboardPage from '@/pages/DashboardPage'
import NotFoundPage from '@/pages/NotFoundPage'
import ForbiddenPage from '@/pages/ForbiddenPage'
import EstatesListPage from '@/pages/estates/EstatesListPage'
import EstateDetailPage from '@/pages/estates/EstateDetailPage'
import StageDetailPage from '@/pages/stages/StageDetailPage'
import UsersPage from '@/pages/admin/UsersPage'
import RegionsPage from '@/pages/admin/RegionsPage'
import DevelopersPage from '@/pages/admin/DevelopersPage'

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/forbidden" element={<ForbiddenPage />} />

      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/estates" element={<EstatesListPage />} />
        <Route path="/estates/:id" element={<EstateDetailPage />} />
        <Route path="/estates/:estateId/stages/:stageId" element={<StageDetailPage />} />
      </Route>

      <Route
        element={
          <ProtectedRoute requiredRoles={['admin']}>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/admin/users" element={<UsersPage />} />
        <Route path="/admin/regions" element={<RegionsPage />} />
        <Route path="/admin/developers" element={<DevelopersPage />} />
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
