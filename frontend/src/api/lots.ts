import { api } from './client'
import type {
  BulkLotCreateResult,
  CsvUploadResult,
  LotInput,
  LotRead,
  LotStatus,
  PaginatedResponse,
  StatusHistoryRead,
  StatusTransitionInput,
} from './types'

export interface ListLotsParams {
  page?: number
  size?: number
  status?: LotStatus | ''
}

export async function listLots(
  stageId: number,
  params: ListLotsParams = {},
): Promise<PaginatedResponse<LotRead>> {
  const query: Record<string, unknown> = { ...params }
  if (query.status === '' || query.status == null) {
    delete query.status
  }
  const { data } = await api.get<PaginatedResponse<LotRead>>(
    `/api/stages/${stageId}/lots`,
    { params: query },
  )
  return data
}

export async function getLot(lotId: number): Promise<LotRead> {
  const { data } = await api.get<LotRead>(`/api/lots/${lotId}`)
  return data
}

export async function createLot(stageId: number, input: LotInput): Promise<LotRead> {
  const { data } = await api.post<LotRead>(`/api/stages/${stageId}/lots`, input)
  return data
}

export async function updateLot(lotId: number, input: Partial<LotInput>): Promise<LotRead> {
  const { data } = await api.patch<LotRead>(`/api/lots/${lotId}`, input)
  return data
}

export async function deleteLot(lotId: number): Promise<void> {
  await api.delete(`/api/lots/${lotId}`)
}

export async function bulkCreateLots(
  stageId: number,
  lots: LotInput[],
): Promise<BulkLotCreateResult> {
  const { data } = await api.post<BulkLotCreateResult>(
    `/api/stages/${stageId}/lots/bulk`,
    { lots },
  )
  return data
}

export async function uploadCsv(stageId: number, file: File): Promise<CsvUploadResult> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post<CsvUploadResult>(
    `/api/stages/${stageId}/lots/upload-csv`,
    form,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  )
  return data
}

export async function transitionStatus(
  lotId: number,
  input: StatusTransitionInput,
): Promise<LotRead> {
  const { data } = await api.post<LotRead>(`/api/lots/${lotId}/status`, input)
  return data
}

export async function getStatusHistory(lotId: number): Promise<StatusHistoryRead[]> {
  const { data } = await api.get<StatusHistoryRead[]>(`/api/lots/${lotId}/status-history`)
  return data
}
