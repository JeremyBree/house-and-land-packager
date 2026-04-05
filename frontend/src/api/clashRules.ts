import { api } from './client'
import type { ClashRuleRead } from './types'

export async function listClashRulesByEstate(estateId: number): Promise<ClashRuleRead[]> {
  const { data } = await api.get<ClashRuleRead[]>(`/api/estates/${estateId}/clash-rules`)
  return data
}

export async function listClashRulesByStage(stageId: number): Promise<ClashRuleRead[]> {
  const { data } = await api.get<ClashRuleRead[]>(`/api/stages/${stageId}/clash-rules`)
  return data
}

export interface ClashRuleInput {
  lot_number: string
  cannot_match: string[]
}

export async function createClashRule(
  estateId: number,
  stageId: number,
  input: ClashRuleInput,
): Promise<ClashRuleRead> {
  const { data } = await api.post<ClashRuleRead>(
    `/api/estates/${estateId}/stages/${stageId}/clash-rules`,
    input,
  )
  return data
}

export async function getClashRule(ruleId: number): Promise<ClashRuleRead> {
  const { data } = await api.get<ClashRuleRead>(`/api/clash-rules/${ruleId}`)
  return data
}

export async function updateClashRule(
  ruleId: number,
  input: Partial<ClashRuleInput>,
): Promise<ClashRuleRead> {
  const { data } = await api.patch<ClashRuleRead>(`/api/clash-rules/${ruleId}`, input)
  return data
}

export async function deleteClashRule(ruleId: number): Promise<void> {
  await api.delete(`/api/clash-rules/${ruleId}`)
}

export interface CopyClashRulesInput {
  target_estate_id: number
  target_stage_id: number
}

export async function copyClashRules(
  stageId: number,
  input: CopyClashRulesInput,
): Promise<{ copied: number }> {
  const { data } = await api.post<{ copied: number }>(
    `/api/stages/${stageId}/clash-rules/copy`,
    input,
  )
  return data
}
