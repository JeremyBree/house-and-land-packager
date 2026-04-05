import { api } from './client'
import type { ConflictRead, ConflictSummary } from './types'

export async function listConflicts(estateId?: number): Promise<ConflictRead[]> {
  const params = estateId ? { estate_id: estateId } : {}
  const { data } = await api.get<ConflictRead[]>('/api/conflicts', { params })
  return data
}

export async function getConflictSummary(): Promise<ConflictSummary> {
  const { data } = await api.get<ConflictSummary>('/api/conflicts/summary')
  return data
}
