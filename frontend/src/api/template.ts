import request from './index'
import type { Template } from '../types'

export function getTemplates() {
  return request.get<Template[]>('/templates')
}

export function getTemplate(id: number) {
  return request.get<Template>(`/templates/${id}`)
}

export function createTemplate(data: {
  name: string
  template_type: string
  content?: string
}) {
  return request.post<Template>('/templates', data)
}

export function updateTemplate(
  id: number,
  data: { name?: string; template_type?: string; content?: string; status?: string },
) {
  return request.put<Template>(`/templates/${id}`, data)
}

export function deleteTemplate(id: number) {
  return request.delete(`/templates/${id}`)
}
