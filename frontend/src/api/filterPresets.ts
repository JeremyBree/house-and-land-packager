import { api } from './client'
import type { FilterPresetCreate, FilterPresetRead, FilterPresetUpdate } from './types'

export async function listPresets(): Promise<FilterPresetRead[]> {
  const { data } = await api.get<FilterPresetRead[]>('/api/filter-presets')
  return data
}

export async function getPreset(id: number): Promise<FilterPresetRead> {
  const { data } = await api.get<FilterPresetRead>(`/api/filter-presets/${id}`)
  return data
}

export async function createPreset(input: FilterPresetCreate): Promise<FilterPresetRead> {
  const { data } = await api.post<FilterPresetRead>('/api/filter-presets', input)
  return data
}

export async function updatePreset(
  id: number,
  body: FilterPresetUpdate,
): Promise<FilterPresetRead> {
  const { data } = await api.patch<FilterPresetRead>(`/api/filter-presets/${id}`, body)
  return data
}

export async function deletePreset(id: number): Promise<void> {
  await api.delete(`/api/filter-presets/${id}`)
}
