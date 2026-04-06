import { api } from './client'
import type { PaginatedResponse } from './types'

export type PricingRequestStatus = 'Pending' | 'Estimating' | 'Priced' | 'In Progress' | 'Completed'

export interface PricingRequestRead {
  request_id: number
  requester_id: number
  estate_id: number
  stage_id: number
  brand: string
  status: PricingRequestStatus
  form_data: Record<string, unknown>
  generated_file_path: string | null
  completed_file_path: string | null
  lot_numbers: string[]
  submitted_at: string | null
  completed_at: string | null
  estimator_id: number | null
  estimated_at: string | null
  site_cost_inputs: Record<string, unknown> | null
  price_breakdown: PriceBreakdownItem[] | null
  created_at: string
  updated_at: string
}

export interface PriceBreakdownItem {
  lot_number: string
  house_name: string
  facade_name: string
  house_price: string
  facade_price: string
  energy_compliance_cost: string
  site_costs_total: string
  design_guidelines_total: string
  extra_landscaping: string
  upgrades_total: string
  discount: string
  discount_reason: string | null
  kdrb_surcharge: string
  total_build_price: string
  total_package_price: string
  land_price: string
  house_fits: boolean
  house_fits_reason: string | null
  line_items: { name: string; amount: string; category: string; detail: string | null }[]
  warnings: string[]
}

export interface PricingRequestDetailRead extends PricingRequestRead {
  requester_name: string | null
  estate_name: string | null
  stage_name: string | null
  estimator_name: string | null
}

export interface LotSiteCostInput {
  lot_number: string
  fall_mm: number
  fill_trees: boolean
  easement_proximity_lhs: boolean
  easement_proximity_rhs: boolean
  retaining_lhs: boolean
  retaining_rhs: boolean
  rock_removal: boolean
  rear_setback_m: string
  existing_neighbours: boolean
  notes: string | null
}

export interface EstimatorSubmission {
  lot_inputs: LotSiteCostInput[]
}

export interface EstimatorAssignment {
  estimator_id: number
}

export interface LotEntry {
  lot_number: string
  house_type: string
  facade_type: string
  garage_side?: string | null
  custom_house_design?: boolean | null
}

export interface PricingRequestCreateInput {
  estate_id: number
  stage_id: number
  brand: string
  has_land_titled: boolean
  titling_when?: string | null
  is_kdrb?: boolean
  is_10_90_deal?: boolean
  developer_land_referrals?: boolean
  building_crossover?: boolean
  shared_crossovers?: boolean
  side_easement?: string | null
  rear_easement?: string | null
  bdm?: string | null
  wholesale_group?: string | null
  lots: LotEntry[]
  notes?: string | null
}

export interface ClashViolation {
  lot_numbers: string[]
  design: string
  facade: string
  rule_id: number | null
  violation_type: string
}

export interface ClashViolationResponse {
  detail: string
  code: string
  violations: ClashViolation[]
}

export interface ListPricingRequestsParams {
  page?: number
  size?: number
  status?: string
  brand?: string
  estate_id?: number
}

export async function listPricingRequests(
  params: ListPricingRequestsParams = {},
): Promise<PaginatedResponse<PricingRequestRead>> {
  const { data } = await api.get<PaginatedResponse<PricingRequestRead>>(
    '/api/pricing-requests',
    { params },
  )
  return data
}

export async function getPricingRequest(id: number): Promise<PricingRequestDetailRead> {
  const { data } = await api.get<PricingRequestDetailRead>(`/api/pricing-requests/${id}`)
  return data
}

export async function createPricingRequest(
  input: PricingRequestCreateInput,
): Promise<PricingRequestRead> {
  const { data } = await api.post<PricingRequestRead>('/api/pricing-requests', input)
  return data
}

export async function downloadGeneratedSheet(id: number): Promise<Blob> {
  const { data } = await api.get(`/api/pricing-requests/${id}/download`, {
    responseType: 'blob',
  })
  return data
}

export async function fulfilPricingRequest(id: number, file: File): Promise<PricingRequestRead> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post<PricingRequestRead>(
    `/api/pricing-requests/${id}/fulfil`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  )
  return data
}

export async function downloadCompletedSheet(id: number): Promise<Blob> {
  const { data } = await api.get(`/api/pricing-requests/${id}/download-completed`, {
    responseType: 'blob',
  })
  return data
}

export async function resubmitPricingRequest(
  id: number,
): Promise<PricingRequestCreateInput> {
  const { data } = await api.post<PricingRequestCreateInput>(
    `/api/pricing-requests/${id}/resubmit`,
  )
  return data
}

export async function deletePricingRequest(id: number): Promise<void> {
  await api.delete(`/api/pricing-requests/${id}`)
}

export async function assignEstimator(
  id: number,
  payload: EstimatorAssignment,
): Promise<PricingRequestRead> {
  const { data } = await api.post<PricingRequestRead>(
    `/api/pricing-requests/${id}/assign-estimator`,
    payload,
  )
  return data
}

export async function submitEstimate(
  id: number,
  payload: EstimatorSubmission,
): Promise<PricingRequestDetailRead> {
  const { data } = await api.post<PricingRequestDetailRead>(
    `/api/pricing-requests/${id}/submit-estimate`,
    payload,
  )
  return data
}

export async function getPriceBreakdown(id: number): Promise<PriceBreakdownItem[]> {
  const { data } = await api.get<PriceBreakdownItem[]>(
    `/api/pricing-requests/${id}/price-breakdown`,
  )
  return data
}

// Pricing Config API
export interface PricingConfigRead {
  config_id: number
  brand: string
  landscaping_rate_per_sqm: string
  base_commission: string
  pct_commission_divisor: string
  kdrb_surcharge: string
  holding_cost_rate: string
  small_lot_threshold_sqm: string
  small_lot_discount: string
  dwellings_discount: string
  corner_block_savings: string
  build_price_rounding: number
  package_price_rounding: number
}

export async function getPricingConfig(brand: string): Promise<PricingConfigRead> {
  const { data } = await api.get<PricingConfigRead>(
    `/api/pricing-config/${encodeURIComponent(brand)}`,
  )
  return data
}

export async function updatePricingConfig(
  brand: string,
  updates: Partial<Omit<PricingConfigRead, 'config_id' | 'brand'>>,
): Promise<PricingConfigRead> {
  const { data } = await api.patch<PricingConfigRead>(
    `/api/pricing-config/${encodeURIComponent(brand)}`,
    updates,
  )
  return data
}
