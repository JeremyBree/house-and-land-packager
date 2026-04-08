import { api } from './client'

// ---- Types -------------------------------------------------------------------

export interface GuidelineTypeRead {
  type_id: number
  short_name: string
  description: string
  sort_order: number
  category_code: string | null
  category_name: string | null
  notes: string | null
  default_price: number
}

export interface GuidelineTypeInput {
  short_name: string
  description: string
  sort_order?: number
  category_code?: string | null
  category_name?: string | null
  notes?: string | null
  default_price?: number
}

export interface EstateGuidelineRead {
  guideline_id: number
  estate_id: number
  stage_id: number | null
  type_id: number
  guideline_type_name: string | null
  cost: number | null
  override_text: string | null
  default_price: number | null
  category_description: string | null
}

export interface EstateGuidelineInput {
  estate_id: number
  stage_id?: number | null
  type_id: number
  cost?: number | null
  override_text?: string | null
}

// ---- Guideline Types ---------------------------------------------------------

export async function listGuidelineTypes(): Promise<GuidelineTypeRead[]> {
  const { data } = await api.get<GuidelineTypeRead[]>('/api/guidelines/types')
  return data
}

export async function createGuidelineType(input: GuidelineTypeInput): Promise<GuidelineTypeRead> {
  const { data } = await api.post<GuidelineTypeRead>('/api/guidelines/types', input)
  return data
}

export async function updateGuidelineType(id: number, input: Partial<GuidelineTypeInput>): Promise<GuidelineTypeRead> {
  const { data } = await api.patch<GuidelineTypeRead>(`/api/guidelines/types/${id}`, input)
  return data
}

export async function deleteGuidelineType(id: number): Promise<void> {
  await api.delete(`/api/guidelines/types/${id}`)
}

// ---- Estate Design Guidelines ------------------------------------------------

export async function listEstateGuidelines(estateId: number, stageId?: number | null): Promise<EstateGuidelineRead[]> {
  const params: Record<string, string> = { estate_id: String(estateId) }
  if (stageId !== undefined && stageId !== null) params.stage_id = String(stageId)
  const { data } = await api.get<EstateGuidelineRead[]>('/api/guidelines/estate', { params })
  return data
}

export async function createEstateGuideline(input: EstateGuidelineInput): Promise<EstateGuidelineRead> {
  const { data } = await api.post<EstateGuidelineRead>('/api/guidelines/estate', input)
  return data
}

export async function updateEstateGuideline(id: number, input: Partial<EstateGuidelineInput>): Promise<EstateGuidelineRead> {
  const { data } = await api.patch<EstateGuidelineRead>(`/api/guidelines/estate/${id}`, input)
  return data
}

export async function deleteEstateGuideline(id: number): Promise<void> {
  await api.delete(`/api/guidelines/estate/${id}`)
}

export async function copyGuidelines(payload: {
  source_estate_id: number
  source_stage_id?: number | null
  target_estate_id: number
  target_stage_id?: number | null
}): Promise<{ copied: number }> {
  const { data } = await api.post<{ copied: number }>('/api/guidelines/estate/copy', payload)
  return data
}
