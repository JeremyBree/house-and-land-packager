import { api } from './client'

export interface ConfigurationRead {
  config_id: number
  config_type: string
  estate_id: number | null
  label: string
  url_or_path: string
  credentials_ref: string | null
  run_schedule: string | null
  enabled: boolean
  priority_rank: number
  notes: string | null
  scraping_config: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface ConfigurationCreate {
  config_type: string
  estate_id?: number | null
  label: string
  url_or_path: string
  credentials_ref?: string | null
  run_schedule?: string | null
  enabled?: boolean
  priority_rank?: number
  notes?: string | null
  scraping_config?: Record<string, unknown>
}

export interface ConfigurationUpdate {
  config_type?: string
  estate_id?: number | null
  label?: string
  url_or_path?: string
  credentials_ref?: string | null
  run_schedule?: string | null
  enabled?: boolean
  priority_rank?: number
  notes?: string | null
  scraping_config?: Record<string, unknown>
}

export async function listConfigurations(params?: {
  type?: string
  enabled?: boolean
}): Promise<ConfigurationRead[]> {
  const { data } = await api.get<ConfigurationRead[]>('/api/configurations', { params })
  return data
}

export async function getConfiguration(id: number): Promise<ConfigurationRead> {
  const { data } = await api.get<ConfigurationRead>(`/api/configurations/${id}`)
  return data
}

export async function createConfiguration(
  input: ConfigurationCreate,
): Promise<ConfigurationRead> {
  const { data } = await api.post<ConfigurationRead>('/api/configurations', input)
  return data
}

export async function updateConfiguration(
  id: number,
  input: ConfigurationUpdate,
): Promise<ConfigurationRead> {
  const { data } = await api.patch<ConfigurationRead>(`/api/configurations/${id}`, input)
  return data
}

export async function deleteConfiguration(id: number): Promise<void> {
  await api.delete(`/api/configurations/${id}`)
}

export async function toggleConfiguration(id: number): Promise<ConfigurationRead> {
  const { data } = await api.post<ConfigurationRead>(`/api/configurations/${id}/toggle`)
  return data
}
