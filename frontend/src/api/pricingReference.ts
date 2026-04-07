import { api } from './client'

// ── Travel Surcharges ─────────────────────────────────────────────

export interface TravelSurchargeRead {
  surcharge_id: number
  suburb_name: string
  postcode: string | null
  surcharge_amount: number
  region_name: string | null
}

export interface TravelSurchargeInput {
  suburb_name: string
  postcode?: string | null
  surcharge_amount: number
  region_name?: string | null
}

export async function listTravelSurcharges(): Promise<TravelSurchargeRead[]> {
  const { data } = await api.get<TravelSurchargeRead[]>('/api/pricing-reference/travel-surcharges')
  return data
}

export async function createTravelSurcharge(input: TravelSurchargeInput): Promise<TravelSurchargeRead> {
  const { data } = await api.post<TravelSurchargeRead>('/api/pricing-reference/travel-surcharges', input)
  return data
}

export async function updateTravelSurcharge(id: number, input: Partial<TravelSurchargeInput>): Promise<TravelSurchargeRead> {
  const { data } = await api.patch<TravelSurchargeRead>(`/api/pricing-reference/travel-surcharges/${id}`, input)
  return data
}

export async function deleteTravelSurcharge(id: number): Promise<void> {
  await api.delete(`/api/pricing-reference/travel-surcharges/${id}`)
}

// ── Site Cost Tiers ───────────────────────────────────────────────

export interface SiteCostTierRead {
  tier_id: number
  tier_name: string
  fall_min_mm: number
  fall_max_mm: number
}

export interface SiteCostTierInput {
  tier_name: string
  fall_min_mm: number
  fall_max_mm: number
}

export async function listSiteCostTiers(): Promise<SiteCostTierRead[]> {
  const { data } = await api.get<SiteCostTierRead[]>('/api/pricing-reference/site-cost-tiers')
  return data
}

export async function createSiteCostTier(input: SiteCostTierInput): Promise<SiteCostTierRead> {
  const { data } = await api.post<SiteCostTierRead>('/api/pricing-reference/site-cost-tiers', input)
  return data
}

export async function updateSiteCostTier(id: number, input: Partial<SiteCostTierInput>): Promise<SiteCostTierRead> {
  const { data } = await api.patch<SiteCostTierRead>(`/api/pricing-reference/site-cost-tiers/${id}`, input)
  return data
}

export async function deleteSiteCostTier(id: number): Promise<void> {
  await api.delete(`/api/pricing-reference/site-cost-tiers/${id}`)
}

// ── Site Cost Items ───────────────────────────────────────────────

export interface SiteCostItemRead {
  item_id: number
  tier_id: number | null
  item_name: string
  condition_type: string | null
  condition_description: string | null
  cost_single_lt190: number | null
  cost_double_lt190: number | null
  cost_single_191_249: number | null
  cost_double_191_249: number | null
  cost_single_250_300: number | null
  cost_double_250_300: number | null
  cost_single_300plus: number | null
  cost_double_300plus: number | null
  sort_order: number
}

export interface SiteCostItemInput {
  tier_id?: number | null
  item_name: string
  condition_type?: string | null
  condition_description?: string | null
  cost_single_lt190?: number | null
  cost_double_lt190?: number | null
  cost_single_191_249?: number | null
  cost_double_191_249?: number | null
  cost_single_250_300?: number | null
  cost_double_250_300?: number | null
  cost_single_300plus?: number | null
  cost_double_300plus?: number | null
  sort_order?: number
}

export async function listSiteCostItems(tierId?: number): Promise<SiteCostItemRead[]> {
  const { data } = await api.get<SiteCostItemRead[]>('/api/pricing-reference/site-cost-items', {
    params: tierId != null ? { tier_id: tierId } : {},
  })
  return data
}

export async function createSiteCostItem(input: SiteCostItemInput): Promise<SiteCostItemRead> {
  const { data } = await api.post<SiteCostItemRead>('/api/pricing-reference/site-cost-items', input)
  return data
}

export async function updateSiteCostItem(id: number, input: Partial<SiteCostItemInput>): Promise<SiteCostItemRead> {
  const { data } = await api.patch<SiteCostItemRead>(`/api/pricing-reference/site-cost-items/${id}`, input)
  return data
}

export async function deleteSiteCostItem(id: number): Promise<void> {
  await api.delete(`/api/pricing-reference/site-cost-items/${id}`)
}

// ── Postcode Site Costs ───────────────────────────────────────────

export interface PostcodeSiteCostRead {
  postcode: string
  rock_removal_cost: number
}

export interface PostcodeSiteCostInput {
  postcode: string
  rock_removal_cost: number
}

export async function listPostcodeCosts(): Promise<PostcodeSiteCostRead[]> {
  const { data } = await api.get<PostcodeSiteCostRead[]>('/api/pricing-reference/postcode-costs')
  return data
}

export async function createPostcodeCost(input: PostcodeSiteCostInput): Promise<PostcodeSiteCostRead> {
  const { data } = await api.post<PostcodeSiteCostRead>('/api/pricing-reference/postcode-costs', input)
  return data
}

export async function updatePostcodeCost(postcode: string, input: { rock_removal_cost: number }): Promise<PostcodeSiteCostRead> {
  const { data } = await api.patch<PostcodeSiteCostRead>(`/api/pricing-reference/postcode-costs/${postcode}`, input)
  return data
}

export async function deletePostcodeCost(postcode: string): Promise<void> {
  await api.delete(`/api/pricing-reference/postcode-costs/${postcode}`)
}

// ── FBC Escalation Bands ─────────────────────────────────────────

export interface FbcEscalationBandRead {
  band_id: number
  brand: string
  day_start: number
  day_end: number
  multiplier: number
}

export interface FbcEscalationBandInput {
  brand: string
  day_start: number
  day_end: number
  multiplier: number
}

export async function listFbcBands(brand?: string): Promise<FbcEscalationBandRead[]> {
  const { data } = await api.get<FbcEscalationBandRead[]>('/api/pricing-reference/fbc-bands', {
    params: brand ? { brand } : {},
  })
  return data
}

export async function createFbcBand(input: FbcEscalationBandInput): Promise<FbcEscalationBandRead> {
  const { data } = await api.post<FbcEscalationBandRead>('/api/pricing-reference/fbc-bands', input)
  return data
}

export async function updateFbcBand(id: number, input: Partial<FbcEscalationBandInput>): Promise<FbcEscalationBandRead> {
  const { data } = await api.patch<FbcEscalationBandRead>(`/api/pricing-reference/fbc-bands/${id}`, input)
  return data
}

export async function deleteFbcBand(id: number): Promise<void> {
  await api.delete(`/api/pricing-reference/fbc-bands/${id}`)
}
