import { api } from './client'
import type { PaginatedResponse } from './types'

export type PricingRequestStatus = 'Pending' | 'In Progress' | 'Completed'

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
  created_at: string
  updated_at: string
}

export interface PricingRequestDetailRead extends PricingRequestRead {
  requester_name: string | null
  estate_name: string | null
  stage_name: string | null
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
