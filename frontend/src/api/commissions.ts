import { api } from './client'

// ---------------------------------------------------------------------------
// Wholesale Groups
// ---------------------------------------------------------------------------

export interface WholesaleGroupRead {
  group_id: number
  group_name: string
  gst_registered: boolean
  active: boolean
}

export interface WholesaleGroupInput {
  group_name: string
  gst_registered?: boolean
  active?: boolean
}

export async function listWholesaleGroups(includeInactive?: boolean): Promise<WholesaleGroupRead[]> {
  const { data } = await api.get<WholesaleGroupRead[]>('/api/wholesale-groups', {
    params: { include_inactive: includeInactive || undefined },
  })
  return data
}

export async function createWholesaleGroup(input: WholesaleGroupInput): Promise<WholesaleGroupRead> {
  const { data } = await api.post<WholesaleGroupRead>('/api/wholesale-groups', input)
  return data
}

export async function updateWholesaleGroup(
  groupId: number,
  input: Partial<WholesaleGroupInput>,
): Promise<WholesaleGroupRead> {
  const { data } = await api.patch<WholesaleGroupRead>(`/api/wholesale-groups/${groupId}`, input)
  return data
}

export async function deleteWholesaleGroup(groupId: number): Promise<void> {
  await api.delete(`/api/wholesale-groups/${groupId}`)
}

// ---------------------------------------------------------------------------
// Commission Rates
// ---------------------------------------------------------------------------

export interface CommissionRateRead {
  rate_id: number
  bdm_profile_id: number
  group_id: number
  commission_fixed: number | null
  commission_pct: number | null
  brand: string
  bdm_name: string | null
  group_name: string | null
}

export interface CommissionRateInput {
  bdm_profile_id: number
  group_id: number
  brand: string
  commission_fixed?: number | null
  commission_pct?: number | null
}

export async function listCommissionRates(
  brand?: string,
  groupId?: number,
): Promise<CommissionRateRead[]> {
  const { data } = await api.get<CommissionRateRead[]>('/api/commission-rates', {
    params: { brand: brand || undefined, group_id: groupId || undefined },
  })
  return data
}

export async function createCommissionRate(input: CommissionRateInput): Promise<CommissionRateRead> {
  const { data } = await api.post<CommissionRateRead>('/api/commission-rates', input)
  return data
}

export async function updateCommissionRate(
  rateId: number,
  input: Partial<CommissionRateInput>,
): Promise<CommissionRateRead> {
  const { data } = await api.patch<CommissionRateRead>(`/api/commission-rates/${rateId}`, input)
  return data
}

export async function deleteCommissionRate(rateId: number): Promise<void> {
  await api.delete(`/api/commission-rates/${rateId}`)
}
