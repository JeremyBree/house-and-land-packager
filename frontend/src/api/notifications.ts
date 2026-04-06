import { api } from './client'
import type { PaginatedResponse } from './types'

export interface NotificationRead {
  notification_id: number
  profile_id: number
  pricing_request_id: number
  title: string
  message: string
  read: boolean
  created_at: string
}

export interface ListNotificationsParams {
  page?: number
  size?: number
}

export async function listNotifications(
  params: ListNotificationsParams = {},
): Promise<PaginatedResponse<NotificationRead>> {
  const { data } = await api.get<PaginatedResponse<NotificationRead>>(
    '/api/notifications',
    { params },
  )
  return data
}

export async function getUnreadCount(): Promise<{ count: number }> {
  const { data } = await api.get<{ count: number }>('/api/notifications/unread-count')
  return data
}

export async function markRead(id: number): Promise<NotificationRead> {
  const { data } = await api.post<NotificationRead>(`/api/notifications/${id}/read`)
  return data
}

export async function markAllRead(): Promise<{ updated: number }> {
  const { data } = await api.post<{ updated: number }>('/api/notifications/read-all')
  return data
}
