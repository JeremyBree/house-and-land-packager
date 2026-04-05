import { api } from './client'
import type { RegionInput, RegionRead } from './types'

export async function listRegions(): Promise<RegionRead[]> {
  const { data } = await api.get<RegionRead[]>('/api/regions')
  return data
}

export async function createRegion(input: RegionInput): Promise<RegionRead> {
  const { data } = await api.post<RegionRead>('/api/regions', input)
  return data
}

export async function updateRegion(id: number, input: RegionInput): Promise<RegionRead> {
  const { data } = await api.patch<RegionRead>(`/api/regions/${id}`, input)
  return data
}

export async function deleteRegion(id: number): Promise<void> {
  await api.delete(`/api/regions/${id}`)
}
