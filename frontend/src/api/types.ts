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
