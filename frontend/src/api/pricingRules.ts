import { api } from './client'
import type {
  GlobalPricingRuleInput,
  GlobalPricingRuleRead,
  PricingRuleCategoryInput,
  PricingRuleCategoryRead,
  StagePricingRuleInput,
  StagePricingRuleRead,
} from './types'

// --- Categories ---

export async function listCategories(brand: string): Promise<PricingRuleCategoryRead[]> {
  const { data } = await api.get<PricingRuleCategoryRead[]>(
    '/api/pricing-rule-categories',
    { params: { brand } },
  )
  return data
}

export async function createCategory(
  input: PricingRuleCategoryInput,
): Promise<PricingRuleCategoryRead> {
  const { data } = await api.post<PricingRuleCategoryRead>(
    '/api/pricing-rule-categories',
    input,
  )
  return data
}

export async function updateCategory(
  categoryId: number,
  input: Partial<PricingRuleCategoryInput>,
): Promise<PricingRuleCategoryRead> {
  const { data } = await api.patch<PricingRuleCategoryRead>(
    `/api/pricing-rule-categories/${categoryId}`,
    input,
  )
  return data
}

export async function deleteCategory(categoryId: number): Promise<void> {
  await api.delete(`/api/pricing-rule-categories/${categoryId}`)
}

// --- Global Rules ---

export async function listGlobalRules(brand: string): Promise<GlobalPricingRuleRead[]> {
  const { data } = await api.get<GlobalPricingRuleRead[]>(
    '/api/pricing-rules/global',
    { params: { brand } },
  )
  return data
}

export async function createGlobalRule(
  input: GlobalPricingRuleInput,
): Promise<GlobalPricingRuleRead> {
  const { data } = await api.post<GlobalPricingRuleRead>(
    '/api/pricing-rules/global',
    input,
  )
  return data
}

export async function getGlobalRule(ruleId: number): Promise<GlobalPricingRuleRead> {
  const { data } = await api.get<GlobalPricingRuleRead>(
    `/api/pricing-rules/global/${ruleId}`,
  )
  return data
}

export async function updateGlobalRule(
  ruleId: number,
  input: Partial<GlobalPricingRuleInput>,
): Promise<GlobalPricingRuleRead> {
  const { data } = await api.patch<GlobalPricingRuleRead>(
    `/api/pricing-rules/global/${ruleId}`,
    input,
  )
  return data
}

export async function deleteGlobalRule(ruleId: number): Promise<void> {
  await api.delete(`/api/pricing-rules/global/${ruleId}`)
}

export async function duplicateGlobalRule(ruleId: number): Promise<GlobalPricingRuleRead> {
  const { data } = await api.post<GlobalPricingRuleRead>(
    `/api/pricing-rules/global/${ruleId}/duplicate`,
  )
  return data
}

// --- Stage Rules ---

export async function listStageRules(
  estateId: number,
  stageId: number,
): Promise<StagePricingRuleRead[]> {
  const { data } = await api.get<StagePricingRuleRead[]>(
    '/api/pricing-rules/stage',
    { params: { estate_id: estateId, stage_id: stageId } },
  )
  return data
}

export async function createStageRule(
  input: StagePricingRuleInput,
): Promise<StagePricingRuleRead> {
  const { data } = await api.post<StagePricingRuleRead>(
    '/api/pricing-rules/stage',
    input,
  )
  return data
}

export async function getStageRule(ruleId: number): Promise<StagePricingRuleRead> {
  const { data } = await api.get<StagePricingRuleRead>(
    `/api/pricing-rules/stage/${ruleId}`,
  )
  return data
}

export async function updateStageRule(
  ruleId: number,
  input: Partial<StagePricingRuleInput>,
): Promise<StagePricingRuleRead> {
  const { data } = await api.patch<StagePricingRuleRead>(
    `/api/pricing-rules/stage/${ruleId}`,
    input,
  )
  return data
}

export async function deleteStageRule(ruleId: number): Promise<void> {
  await api.delete(`/api/pricing-rules/stage/${ruleId}`)
}

export async function duplicateStageRule(ruleId: number): Promise<StagePricingRuleRead> {
  const { data } = await api.post<StagePricingRuleRead>(
    `/api/pricing-rules/stage/${ruleId}/duplicate`,
  )
  return data
}
