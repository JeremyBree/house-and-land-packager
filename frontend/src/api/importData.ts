import { api } from './client'

export interface ImportResult {
  houses_created: number
  facades_created: number
  energy_ratings_created: number
  upgrades_created: number
  upgrade_categories_created: number
  wholesale_groups_created: number
  commission_rates_created: number
  travel_surcharges_created: number
  postcode_costs_created: number
  guideline_types_created: number
  estate_guidelines_created: number
  fbc_bands_created: number
  site_cost_tiers_created: number
  site_cost_items_created: number
  skipped: number
  errors: string[]
}

export async function importPricingWorkbook(
  file: File,
  brand: string,
): Promise<ImportResult> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post<ImportResult>(
    `/api/admin/import-pricing-workbook?brand=${encodeURIComponent(brand)}`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  )
  return data
}

// ---- Bulk Seed ---------------------------------------------------------------

export interface SeedEstatesResult {
  estates_created: number
  stages_created: number
  skipped: number
  errors: { row: number; error: string }[]
}

export interface SeedGuidelinesResult {
  created: number
  skipped: number
  errors: { row: number; error: string }[]
}

export async function seedEstatesStages(): Promise<SeedEstatesResult> {
  const { data } = await api.post<SeedEstatesResult>('/api/admin/seed-estates-stages')
  return data
}

export async function seedEstateGuidelines(): Promise<SeedGuidelinesResult> {
  const { data } = await api.post<SeedGuidelinesResult>(
    '/api/admin/seed-estate-guidelines',
    undefined,
    { timeout: 300_000 },
  )
  return data
}

export async function uploadEstatesStagesCsv(file: File): Promise<SeedEstatesResult> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post<SeedEstatesResult>(
    '/api/estates/upload-csv',
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  )
  return data
}
