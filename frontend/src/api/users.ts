import { api } from './client'
import type {
  PaginatedResponse,
  UserCreateInput,
  UserRead,
  UserRoleType,
  UserUpdateInput,
} from './types'

export interface ListUsersParams {
  page?: number
  size?: number
  search?: string
}

export async function listUsers(params: ListUsersParams = {}): Promise<PaginatedResponse<UserRead>> {
  const { data } = await api.get<PaginatedResponse<UserRead>>('/api/users', { params })
  return data
}

export async function createUser(input: UserCreateInput): Promise<UserRead> {
  const { data } = await api.post<UserRead>('/api/users', input)
  return data
}

export async function getUser(id: number): Promise<UserRead> {
  const { data } = await api.get<UserRead>(`/api/users/${id}`)
  return data
}

export async function updateUser(id: number, input: UserUpdateInput): Promise<UserRead> {
  const { data } = await api.patch<UserRead>(`/api/users/${id}`, input)
  return data
}

export async function updateUserRoles(id: number, roles: UserRoleType[]): Promise<UserRead> {
  const { data } = await api.put<UserRead>(`/api/users/${id}/roles`, { roles })
  return data
}

export async function deleteUser(id: number): Promise<void> {
  await api.delete(`/api/users/${id}`)
}
