import { api } from './client'
import type { PricingTemplateRead } from './types'

export async function listTemplates(): Promise<PricingTemplateRead[]> {
  const { data } = await api.get<PricingTemplateRead[]>('/api/pricing-templates')
  return data
}

export async function getTemplateByBrand(brand: string): Promise<PricingTemplateRead> {
  const { data } = await api.get<PricingTemplateRead>(`/api/pricing-templates/${brand}`)
  return data
}

export async function uploadTemplate(
  brand: string,
  file: File,
): Promise<PricingTemplateRead> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post<PricingTemplateRead>(
    `/api/pricing-templates/${brand}/upload`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  )
  return data
}

export interface TemplateMappingsUpdate {
  sheet_name?: string | null
  data_start_row?: number | null
  header_mappings?: Record<string, { row: number; col: number }> | null
  column_mappings?: Record<string, number> | null
}

export async function updateMappings(
  templateId: number,
  body: TemplateMappingsUpdate,
): Promise<PricingTemplateRead> {
  const { data } = await api.patch<PricingTemplateRead>(
    `/api/pricing-templates/${templateId}/mappings`,
    body,
  )
  return data
}

export interface DataValidationsResponse {
  validations: Record<string, string[]>
}

export async function getValidations(brand: string): Promise<DataValidationsResponse> {
  const { data } = await api.get<DataValidationsResponse>(
    `/api/pricing-templates/${brand}/validations`,
  )
  return data
}
