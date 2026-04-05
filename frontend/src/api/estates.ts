import { api } from './client'
import type {
  EstateDetailRead,
  EstateInput,
  EstateRead,
  PaginatedResponse,
} from './types'

export interface ListEstatesParams {
  page?: number
  size?: number
  search?: string
  developer_id?: number
  region_id?: number
  active?: boolean
}

export async function listEstates(params: ListEstatesParams = {}): Promise<PaginatedResponse<EstateRead>> {
  const { data } = await api.get<PaginatedResponse<EstateRead>>('/api/estates', { params })
  return data
}

export async function getEstate(id: number): Promise<EstateDetailRead> {
  const { data } = await api.get<EstateDetailRead>(`/api/estates/${id}`)
  return data
}

export async function createEstate(input: EstateInput): Promise<EstateRead> {
  const { data } = await api.post<EstateRead>('/api/estates', input)
  return data
}

export async function updateEstate(id: number, input: Partial<EstateInput>): Promise<EstateRead> {
  const { data } = await api.patch<EstateRead>(`/api/estates/${id}`, input)
  return data
}

export async function deleteEstate(id: number): Promise<void> {
  await api.delete(`/api/estates/${id}`)
}
