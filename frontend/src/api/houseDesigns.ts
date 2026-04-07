import { api } from './client'

export interface HouseFacadeRead {
  facade_id: number
  design_id: number
  facade_name: string
  facade_price: number
  facade_details: string | null
  is_included: boolean
}

export interface HouseFacadeInput {
  facade_name: string
  facade_price: number
  facade_details?: string | null
  is_included?: boolean
}

export interface HouseDesignRead {
  design_id: number
  brand: string
  house_name: string
  base_price: number
  storey: string
  frontage: number
  depth: number
  gf_sqm: number
  total_sqm: number
  lot_total_sqm: number
  squares: number
  details: string | null
  effective_date: string | null
  active: boolean
  facades: HouseFacadeRead[]
}

export interface HouseDesignInput {
  brand: string
  house_name: string
  base_price: number
  storey: string
  frontage: number
  depth: number
  gf_sqm: number
  total_sqm: number
  lot_total_sqm: number
  squares: number
  details?: string | null
  effective_date?: string | null
  active?: boolean
}

export async function listHouseDesigns(
  brand: string,
  includeInactive?: boolean,
): Promise<HouseDesignRead[]> {
  const { data } = await api.get<HouseDesignRead[]>('/api/house-designs', {
    params: { brand, include_inactive: includeInactive || undefined },
  })
  return data
}

export async function getHouseDesign(designId: number): Promise<HouseDesignRead> {
  const { data } = await api.get<HouseDesignRead>(`/api/house-designs/${designId}`)
  return data
}

export async function createHouseDesign(input: HouseDesignInput): Promise<HouseDesignRead> {
  const { data } = await api.post<HouseDesignRead>('/api/house-designs', input)
  return data
}

export async function updateHouseDesign(
  designId: number,
  input: Partial<HouseDesignInput>,
): Promise<HouseDesignRead> {
  const { data } = await api.patch<HouseDesignRead>(
    `/api/house-designs/${designId}`,
    input,
  )
  return data
}

export async function deleteHouseDesign(designId: number): Promise<void> {
  await api.delete(`/api/house-designs/${designId}`)
}

// Facades
export async function listFacades(designId: number): Promise<HouseFacadeRead[]> {
  const { data } = await api.get<HouseFacadeRead[]>(
    `/api/house-designs/${designId}/facades`,
  )
  return data
}

export async function createFacade(
  designId: number,
  input: HouseFacadeInput,
): Promise<HouseFacadeRead> {
  const { data } = await api.post<HouseFacadeRead>(
    `/api/house-designs/${designId}/facades`,
    input,
  )
  return data
}

export async function updateFacade(
  designId: number,
  facadeId: number,
  input: Partial<HouseFacadeInput>,
): Promise<HouseFacadeRead> {
  const { data } = await api.patch<HouseFacadeRead>(
    `/api/house-designs/${designId}/facades/${facadeId}`,
    input,
  )
  return data
}

export async function deleteFacade(
  designId: number,
  facadeId: number,
): Promise<void> {
  await api.delete(`/api/house-designs/${designId}/facades/${facadeId}`)
}

// Energy Ratings
export interface EnergyRatingRead {
  rating_id: number
  design_id: number
  garage_side: string
  orientation: string
  star_rating: number
  best_worst: string
  compliance_cost: number
}

export interface EnergyRatingInput {
  garage_side: string
  orientation: string
  star_rating: number
  best_worst: string
  compliance_cost: number
}

export async function listEnergyRatings(designId: number): Promise<EnergyRatingRead[]> {
  const { data } = await api.get<EnergyRatingRead[]>(
    `/api/house-designs/${designId}/energy-ratings`,
  )
  return data
}

export async function createEnergyRating(
  designId: number,
  input: EnergyRatingInput,
): Promise<EnergyRatingRead> {
  const { data } = await api.post<EnergyRatingRead>(
    `/api/house-designs/${designId}/energy-ratings`,
    input,
  )
  return data
}

export async function updateEnergyRating(
  designId: number,
  ratingId: number,
  input: Partial<EnergyRatingInput>,
): Promise<EnergyRatingRead> {
  const { data } = await api.patch<EnergyRatingRead>(
    `/api/house-designs/${designId}/energy-ratings/${ratingId}`,
    input,
  )
  return data
}

export async function deleteEnergyRating(
  designId: number,
  ratingId: number,
): Promise<void> {
  await api.delete(`/api/house-designs/${designId}/energy-ratings/${ratingId}`)
}
