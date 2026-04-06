import { api } from './client'
import type { PaginatedResponse } from './types'

export interface IngestionLogRead {
  log_id: number
  agent_type: string
  source_identifier: string
  run_timestamp: string
  records_found: number
  records_created: number
  records_updated: number
  records_deactivated: number
  status: string
  error_detail: string | null
}

export interface ListIngestionLogsParams {
  page?: number
  size?: number
  agent_type?: string
  status?: string
}

export async function listIngestionLogs(
  params: ListIngestionLogsParams = {},
): Promise<PaginatedResponse<IngestionLogRead>> {
  const { data } = await api.get<PaginatedResponse<IngestionLogRead>>(
    '/api/ingestion-logs',
    { params },
  )
  return data
}

export async function getIngestionLog(id: number): Promise<IngestionLogRead> {
  const { data } = await api.get<IngestionLogRead>(`/api/ingestion-logs/${id}`)
  return data
}
