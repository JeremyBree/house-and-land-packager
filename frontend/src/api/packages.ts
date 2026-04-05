import { api } from './client'
import type { PackageInput, PackageRead, PaginatedResponse } from './types'

export interface ListPackagesParams {
  estate_id?: number
  stage_id?: number
  brand?: string
  design?: string
  facade?: string
  lot_number?: string
  page?: number
  size?: number
}

export async function listPackages(
  params: ListPackagesParams = {},
): Promise<PaginatedResponse<PackageRead>> {
  const { data } = await api.get<PaginatedResponse<PackageRead>>('/api/packages', { params })
  return data
}

export async function createPackage(input: PackageInput): Promise<PackageRead> {
  const { data } = await api.post<PackageRead>('/api/packages', input)
  return data
}

export async function getPackage(id: number): Promise<PackageRead> {
  const { data } = await api.get<PackageRead>(`/api/packages/${id}`)
  return data
}

export async function updatePackage(
  id: number,
  input: Partial<PackageInput>,
): Promise<PackageRead> {
  const { data } = await api.patch<PackageRead>(`/api/packages/${id}`, input)
  return data
}

export async function deletePackage(id: number): Promise<void> {
  await api.delete(`/api/packages/${id}`)
}

export async function uploadFlyer(id: number, file: File): Promise<PackageRead> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post<PackageRead>(`/api/packages/${id}/flyer`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function deleteFlyer(id: number): Promise<void> {
  await api.delete(`/api/packages/${id}/flyer`)
}
