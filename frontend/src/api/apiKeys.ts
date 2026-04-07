import { api } from './client'

export interface ApiKeyRead {
  key_id: number
  key_prefix: string
  agent_name: string
  agent_type: string
  scopes: string
  is_active: boolean
  last_used_at: string | null
  expires_at: string | null
  created_by: number
  notes: string | null
  created_at: string
  updated_at: string
}

export interface ApiKeyCreateInput {
  agent_name: string
  agent_type: string
  scopes: string
  expires_at?: string | null
  notes?: string | null
}

export interface ApiKeyCreateResponse extends ApiKeyRead {
  raw_key: string
}

export interface ApiKeyUpdate {
  agent_name?: string
  agent_type?: string
  scopes?: string
  is_active?: boolean
  notes?: string | null
}

export async function listApiKeys(): Promise<ApiKeyRead[]> {
  const { data } = await api.get<ApiKeyRead[]>('/api/api-keys')
  return data
}

export async function createApiKey(input: ApiKeyCreateInput): Promise<ApiKeyCreateResponse> {
  const { data } = await api.post<ApiKeyCreateResponse>('/api/api-keys', input)
  return data
}

export async function updateApiKey(id: number, input: ApiKeyUpdate): Promise<ApiKeyRead> {
  const { data } = await api.patch<ApiKeyRead>(`/api/api-keys/${id}`, input)
  return data
}

export async function deleteApiKey(id: number): Promise<void> {
  await api.delete(`/api/api-keys/${id}`)
}

export async function revokeApiKey(id: number): Promise<ApiKeyRead> {
  const { data } = await api.post<ApiKeyRead>(`/api/api-keys/${id}/revoke`)
  return data
}
