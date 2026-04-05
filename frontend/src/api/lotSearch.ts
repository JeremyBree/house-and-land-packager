import { api } from './client'
import type { LotSearchFilters, LotSearchRequest, LotSearchResponse } from './types'

export async function searchLots(request: LotSearchRequest): Promise<LotSearchResponse> {
  const { data } = await api.post<LotSearchResponse>('/api/lots/search', request)
  return data
}

export async function exportCsv(filters: LotSearchFilters): Promise<Blob> {
  const { data } = await api.post<Blob>('/api/lots/export/csv', filters, {
    responseType: 'blob',
  })
  return data
}

export async function exportXlsx(filters: LotSearchFilters): Promise<Blob> {
  const { data } = await api.post<Blob>('/api/lots/export/xlsx', filters, {
    responseType: 'blob',
  })
  return data
}
