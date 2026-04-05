import { api } from './client'
import type { StageDetailRead, StageInput, StageRead } from './types'

export async function listStages(estateId: number): Promise<StageRead[]> {
  const { data } = await api.get<StageRead[]>(`/api/estates/${estateId}/stages`)
  return data
}

export async function getStage(stageId: number): Promise<StageDetailRead> {
  const { data } = await api.get<StageDetailRead>(`/api/stages/${stageId}`)
  return data
}

export async function createStage(estateId: number, input: StageInput): Promise<StageRead> {
  const { data } = await api.post<StageRead>(`/api/estates/${estateId}/stages`, input)
  return data
}

export async function updateStage(stageId: number, input: Partial<StageInput>): Promise<StageRead> {
  const { data } = await api.patch<StageRead>(`/api/stages/${stageId}`, input)
  return data
}

export async function deleteStage(stageId: number): Promise<void> {
  await api.delete(`/api/stages/${stageId}`)
}
