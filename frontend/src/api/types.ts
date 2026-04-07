export type UserRoleType = 'admin' | 'pricing' | 'sales' | 'requester'

export const USER_ROLES: UserRoleType[] = ['admin', 'pricing', 'sales', 'requester']

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface UserRead {
  profile_id: number
  email: string
  first_name: string
  last_name: string
  job_title: string | null
  email_verified: boolean
  roles: UserRoleType[]
  created_at: string
}

export interface UserCreateInput {
  email: string
  password: string
  first_name: string
  last_name: string
  job_title?: string | null
  roles: UserRoleType[]
}

export interface UserUpdateInput {
  first_name?: string
  last_name?: string
  job_title?: string | null
}

export interface RegionRead {
  region_id: number
  name: string
  created_at: string
}

export interface RegionInput {
  name: string
}

export interface DeveloperRead {
  developer_id: number
  developer_name: string
  developer_website: string | null
  contact_email: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface DeveloperInput {
  developer_name: string
  developer_website?: string | null
  contact_email?: string | null
  notes?: string | null
}

export interface EstateRead {
  estate_id: number
  developer_id: number
  region_id: number | null
  estate_name: string
  suburb: string | null
  state: string | null
  postcode: string | null
  contact_name: string | null
  contact_mobile: string | null
  contact_email: string | null
  description: string | null
  notes: string | null
  active: boolean
  created_at: string
  updated_at: string
}

export interface EstateDetailRead extends EstateRead {
  developer: DeveloperRead
  region: RegionRead | null
}

export interface EstateInput {
  developer_id: number
  region_id?: number | null
  estate_name: string
  suburb?: string | null
  state?: string | null
  postcode?: string | null
  contact_name?: string | null
  contact_mobile?: string | null
  contact_email?: string | null
  description?: string | null
  notes?: string | null
  active?: boolean
}

export type StageStatus = 'Active' | 'Upcoming' | 'Completed'
export const STAGE_STATUSES: StageStatus[] = ['Active', 'Upcoming', 'Completed']

export type LotStatus = 'Available' | 'Unavailable' | 'Hold' | 'Deposit Taken' | 'Sold'
export const LOT_STATUSES: LotStatus[] = [
  'Available',
  'Unavailable',
  'Hold',
  'Deposit Taken',
  'Sold',
]

export type LotOrientation = 'N' | 'NE' | 'E' | 'SE' | 'S' | 'SW' | 'W' | 'NW'
export const LOT_ORIENTATIONS: LotOrientation[] = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']

export interface StageRead {
  stage_id: number
  estate_id: number
  name: string
  lot_count: number | null
  status: StageStatus
  release_date: string | null
  created_at: string
  updated_at: string
}

export interface StageDetailRead extends StageRead {
  lot_count_actual: number
  status_breakdown: Record<string, number>
}

export interface StageInput {
  name: string
  lot_count?: number | null
  status: StageStatus
  release_date?: string | null
}

export interface LotRead {
  lot_id: number
  stage_id: number
  lot_number: string
  frontage: string | null
  depth: string | null
  size_sqm: string | null
  corner_block: boolean
  orientation: string | null
  side_easement: string | null
  rear_easement: string | null
  street_name: string | null
  land_price: string | null
  build_price: string | null
  package_price: string | null
  design: string | null
  facade: string | null
  brand: string | null
  status: LotStatus
  substation: boolean
  title_date: string | null
  last_confirmed_date: string | null
  source: string | null
  source_detail: string | null
  created_at: string
  updated_at: string
}

export interface LotInput {
  lot_number: string
  frontage?: string | null
  depth?: string | null
  size_sqm?: string | null
  corner_block?: boolean
  orientation?: string | null
  side_easement?: string | null
  rear_easement?: string | null
  street_name?: string | null
  land_price?: string | null
  build_price?: string | null
  package_price?: string | null
  substation?: boolean
  title_date?: string | null
}

export interface StatusHistoryRead {
  history_id: number
  lot_id: number
  previous_status: LotStatus | null
  new_status: LotStatus
  changed_at: string
  triggering_agent: string
  source_detail: string | null
}

export interface StatusTransitionInput {
  new_status: LotStatus
  reason: string
}

export interface DocumentRead {
  document_id: number
  estate_id: number
  stage_id: number | null
  file_name: string
  file_type: string
  file_size: number
  description: string | null
  created_at: string
  download_url: string
}

export interface CsvUploadResult {
  created: number
  skipped: number
  errors: Array<{ row: number; error: string }>
}

export interface BulkLotCreateResult {
  created: number
  skipped: number
  errors: Array<{ row: number; error: string }>
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ErrorResponse {
  detail: string
  code?: string
}

export interface LotSearchFilters {
  estate_ids?: number[] | null
  developer_ids?: number[] | null
  region_ids?: number[] | null
  suburbs?: string[] | null
  statuses?: LotStatus[] | null
  price_min?: string | null
  price_max?: string | null
  size_min?: string | null
  size_max?: string | null
  frontage_min?: string | null
  depth_min?: string | null
  corner_block?: boolean | null
  title_date_from?: string | null
  title_date_to?: string | null
  exclude_null_price?: boolean
  text_search?: string | null
}

export type LotSearchSortBy =
  | 'land_price'
  | 'size_sqm'
  | 'frontage'
  | 'lot_number'
  | 'estate_name'
  | 'last_confirmed_date'

export interface LotSearchRequest {
  filters: LotSearchFilters
  page: number
  size: number
  sort_by: LotSearchSortBy
  sort_desc: boolean
}

export interface LotSearchResult extends LotRead {
  estate_name: string
  estate_suburb: string | null
  estate_state: string | null
  developer_name: string
  region_name: string | null
  stage_name: string
}

export interface LotSearchResponse {
  items: LotSearchResult[]
  total: number
  page: number
  size: number
  pages: number
  filter_summary: Record<string, unknown>
}

export interface FilterPresetRead {
  preset_id: number
  profile_id: number
  name: string
  filters: LotSearchFilters
  created_at: string
  updated_at: string
}

export interface FilterPresetCreate {
  name: string
  filters: LotSearchFilters
}

export interface FilterPresetUpdate {
  name?: string
  filters?: LotSearchFilters
}

export interface ClashRuleRead {
  rule_id: number
  estate_id: number
  stage_id: number
  lot_number: string
  cannot_match: string[]
  created_at: string
}

export interface PackageRead {
  package_id: number
  estate_id: number
  stage_id: number
  lot_number: string
  design: string
  facade: string
  colour_scheme: string | null
  brand: string
  source: string | null
  status: string | null
  flyer_path: string | null
  created_at: string
  updated_at: string
  estate_name: string | null
  stage_name: string | null
  lot_id: number | null
}

export interface PackageInput {
  estate_id: number
  stage_id: number
  lot_number: string
  design: string
  facade: string
  colour_scheme?: string | null
  brand: string
  source?: string | null
  status?: string | null
}

export interface ConflictRead {
  conflict_type: 'design-facade' | 'design-facade-colour'
  severity: 'high' | 'critical'
  package_a: PackageRead
  package_b: PackageRead
  rule_id: number
  estate_id: number
  stage_id: number
  lot_numbers: string[]
}

export interface ConflictSummary {
  total_conflicts: number
  by_type: Record<string, number>
  by_estate: Array<{ estate_id: number; estate_name: string; count: number }>
}

// --- Sprint 5: Pricing Templates & Rules ---

export interface PricingTemplateRead {
  template_id: number
  brand: string
  file_path: string
  sheet_name: string
  data_start_row: number
  header_mappings: Record<string, { row: number; col: number }>
  column_mappings: Record<string, number>
  data_validations: Record<string, string[]>
  created_at: string
  updated_at: string
}

export interface PricingRuleCategoryRead {
  category_id: number
  name: string
  brand: string
  sort_order: number
}

export interface PricingRuleCategoryInput {
  name: string
  brand: string
  sort_order?: number
}

export interface GlobalPricingRuleRead {
  rule_id: number
  brand: string
  item_name: string
  cost: string
  condition: string | null
  condition_value: string | null
  cell_row: number
  cell_col: number
  cost_cell_row: number
  cost_cell_col: number
  category_id: number | null
  sort_order: number
  created_at: string
  updated_at: string
  category_name?: string | null
}

export interface GlobalPricingRuleInput {
  brand: string
  item_name: string
  cost: string
  condition?: string | null
  condition_value?: string | null
  cell_row: number
  cell_col: number
  cost_cell_row: number
  cost_cell_col: number
  category_id?: number | null
  sort_order?: number
}

export interface StagePricingRuleRead extends GlobalPricingRuleRead {
  estate_id: number
  stage_id: number
  estate_name?: string | null
  stage_name?: string | null
}

export interface StagePricingRuleInput extends GlobalPricingRuleInput {
  estate_id: number
  stage_id: number
}
