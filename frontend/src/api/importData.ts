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
