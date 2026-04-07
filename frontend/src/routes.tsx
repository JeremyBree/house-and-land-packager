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
import ConfigurationsPage from '@/pages/admin/ConfigurationsPage'
import IngestionLogsPage from '@/pages/admin/IngestionLogsPage'
import PricingConfigPage from '@/pages/admin/PricingConfigPage'
import HouseDesignsPage from '@/pages/admin/HouseDesignsPage'
import EnergyRatingsPage from '@/pages/admin/EnergyRatingsPage'
import CommissionsPage from '@/pages/admin/CommissionsPage'
import TravelSurchargesPage from '@/pages/admin/TravelSurchargesPage'
import SiteCostsPage from '@/pages/admin/SiteCostsPage'
import PostcodeCostsPage from '@/pages/admin/PostcodeCostsPage'
import FbcBandsPage from '@/pages/admin/FbcBandsPage'
import UpgradesPage from '@/pages/admin/UpgradesPage'
import EstateGuidelinesPage from '@/pages/admin/EstateGuidelinesPage'
import PdfIngestionPage from '@/pages/PdfIngestionPage'
import ApiKeysPage from '@/pages/admin/ApiKeysPage'
import ImportDataPage from '@/pages/admin/ImportDataPage'

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
        <Route path="/pdf-ingestion" element={<PdfIngestionPage />} />
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
        <Route path="/admin/configurations" element={<ConfigurationsPage />} />
        <Route path="/admin/ingestion-logs" element={<IngestionLogsPage />} />
        <Route path="/admin/pricing-config" element={<PricingConfigPage />} />
        <Route path="/admin/house-designs" element={<HouseDesignsPage />} />
        <Route path="/admin/energy-ratings" element={<EnergyRatingsPage />} />
        <Route path="/admin/commissions" element={<CommissionsPage />} />
        <Route path="/admin/travel-surcharges" element={<TravelSurchargesPage />} />
        <Route path="/admin/site-costs" element={<SiteCostsPage />} />
        <Route path="/admin/postcode-costs" element={<PostcodeCostsPage />} />
        <Route path="/admin/fbc-bands" element={<FbcBandsPage />} />
        <Route path="/admin/upgrades" element={<UpgradesPage />} />
        <Route path="/admin/estate-guidelines" element={<EstateGuidelinesPage />} />
        <Route path="/admin/api-keys" element={<ApiKeysPage />} />
        <Route path="/admin/import-data" element={<ImportDataPage />} />
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
