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
import LsiPage from '@/pages/lsi/LsiPage'
import PackagesPage from '@/pages/packages/PackagesPage'
import ConflictsPage from '@/pages/conflicts/ConflictsPage'
import PricingRequestsPage from '@/pages/pricing/PricingRequestsPage'
import PricingRequestFormPage from '@/pages/pricing/PricingRequestFormPage'
import PricingRequestDetailPage from '@/pages/pricing/PricingRequestDetailPage'
import NotificationsPage from '@/pages/notifications/NotificationsPage'
import UsersPage from '@/pages/admin/UsersPage'
import RegionsPage from '@/pages/admin/RegionsPage'
import DevelopersPage from '@/pages/admin/DevelopersPage'
import PricingTemplatesPage from '@/pages/admin/PricingTemplatesPage'
import PricingRulesPage from '@/pages/admin/PricingRulesPage'
import StageRulesPage from '@/pages/admin/StageRulesPage'

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
        <Route path="/packages" element={<PackagesPage />} />
        <Route path="/conflicts" element={<ConflictsPage />} />
        <Route path="/pricing-requests" element={<PricingRequestsPage />} />
        <Route path="/pricing-requests/new" element={<PricingRequestFormPage />} />
        <Route path="/pricing-requests/:id" element={<PricingRequestDetailPage />} />
        <Route path="/notifications" element={<NotificationsPage />} />
        <Route path="/lsi" element={<LsiPage />} />
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
        <Route path="/admin/pricing-templates" element={<PricingTemplatesPage />} />
        <Route path="/admin/pricing-rules" element={<PricingRulesPage />} />
        <Route path="/admin/stage-rules" element={<StageRulesPage />} />
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
