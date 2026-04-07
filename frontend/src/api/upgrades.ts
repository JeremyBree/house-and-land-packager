import { api } from './client'

// ---- Types -------------------------------------------------------------------

export interface UpgradeCategoryRead {
  category_id: number
  brand: string
  name: string
  sort_order: number
}

export interface UpgradeCategoryInput {
  brand: string
  name: string
  sort_order?: number
}

export interface UpgradeItemRead {
  upgrade_id: number
  brand: string
  category_id: number | null
  category_name: string | null
  description: string
  price: number
  date_added: string | null
  notes: string | null
  sort_order: number
  created_at: string
  updated_at: string
}

export interface UpgradeItemInput {
  brand: string
  category_id?: number | null
  description: string
  price: number
  date_added?: string | null
  notes?: string | null
  sort_order?: number
}

// ---- Categories --------------------------------------------------------------

export async function listUpgradeCategories(brand?: string): Promise<UpgradeCategoryRead[]> {
  const params: Record<string, string> = {}
  if (brand) params.brand = brand
  const { data } = await api.get<UpgradeCategoryRead[]>('/api/upgrades/categories', { params })
  return data
}

export async function createUpgradeCategory(input: UpgradeCategoryInput): Promise<UpgradeCategoryRead> {
  const { data } = await api.post<UpgradeCategoryRead>('/api/upgrades/categories', input)
  return data
}

export async function updateUpgradeCategory(id: number, input: Partial<UpgradeCategoryInput>): Promise<UpgradeCategoryRead> {
  const { data } = await api.patch<UpgradeCategoryRead>(`/api/upgrades/categories/${id}`, input)
  return data
}

export async function deleteUpgradeCategory(id: number): Promise<void> {
  await api.delete(`/api/upgrades/categories/${id}`)
}

// ---- Items -------------------------------------------------------------------

export async function listUpgradeItems(brand?: string, categoryId?: number): Promise<UpgradeItemRead[]> {
  const params: Record<string, string> = {}
  if (brand) params.brand = brand
  if (categoryId !== undefined && categoryId !== null) params.category_id = String(categoryId)
  const { data } = await api.get<UpgradeItemRead[]>('/api/upgrades/items', { params })
  return data
}

export async function createUpgradeItem(input: UpgradeItemInput): Promise<UpgradeItemRead> {
  const { data } = await api.post<UpgradeItemRead>('/api/upgrades/items', input)
  return data
}

export async function updateUpgradeItem(id: number, input: Partial<UpgradeItemInput>): Promise<UpgradeItemRead> {
  const { data } = await api.patch<UpgradeItemRead>(`/api/upgrades/items/${id}`, input)
  return data
}

export async function deleteUpgradeItem(id: number): Promise<void> {
  await api.delete(`/api/upgrades/items/${id}`)
}
