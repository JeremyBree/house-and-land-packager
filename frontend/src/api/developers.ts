import { api } from './client'
import type { DeveloperInput, DeveloperRead } from './types'

export async function listDevelopers(): Promise<DeveloperRead[]> {
  const { data } = await api.get<DeveloperRead[]>('/api/developers')
  return data
}

export async function createDeveloper(input: DeveloperInput): Promise<DeveloperRead> {
  const { data } = await api.post<DeveloperRead>('/api/developers', input)
  return data
}

export async function updateDeveloper(id: number, input: Partial<DeveloperInput>): Promise<DeveloperRead> {
  const { data } = await api.patch<DeveloperRead>(`/api/developers/${id}`, input)
  return data
}

export async function deleteDeveloper(id: number): Promise<void> {
  await api.delete(`/api/developers/${id}`)
}
