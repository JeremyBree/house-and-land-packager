import { api } from './client'

export interface RecentRequest {
  request_id: number
  brand: string
  status: string
  estate_name: string | null
  stage_name: string | null
  lot_count: number
  created_at: string
}

export interface DashboardData {
  total_estates: number
  total_lots: number
  total_packages: number
  active_conflicts: number
  pending_requests: number
  lot_status_breakdown: Record<string, number>
  recent_requests: RecentRequest[]
}

export async function getDashboard(): Promise<DashboardData> {
  const { data } = await api.get<DashboardData>('/api/dashboard')
  return data
}
