import request from './index'
import type { User, LogOut } from '../types'

export function getAdminUsers() {
  return request.get<User[]>('/admin/users')
}

export function updateAdminUser(
  id: number,
  data: { full_name?: string; email?: string; role?: string; status?: number },
) {
  return request.put<User>(`/admin/users/${id}`, data)
}

export function disableAdminUser(id: number) {
  return request.delete(`/admin/users/${id}`)
}

export function getAdminLogs(params: {
  log_type?: string
  module_name?: string
  result_status?: string
  page?: number
  page_size?: number
}) {
  return request.get<{
    items: LogOut[]
    total: number
    page: number
    page_size: number
  }>('/admin/logs', { params })
}
