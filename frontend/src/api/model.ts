import request from './index'
import type { SysModel, ModelElement, ElementTreeItem } from '../types'

export function getModels(project_id?: number) {
  const params = project_id ? { project_id } : {}
  return request.get<SysModel[]>('/models', { params })
}

export function getModel(id: number) {
  return request.get<SysModel>(`/models/${id}`)
}

export function uploadModel(formData: FormData) {
  return request.post<SysModel>('/models/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function deleteModel(id: number) {
  return request.delete(`/models/${id}`)
}

export function getModelTree(modelId: number) {
  return request.get<ElementTreeItem[]>(`/models/${modelId}/elements/tree`)
}

export function getModelElements(modelId: number) {
  return request.get<ModelElement[]>(`/models/${modelId}/elements`)
}

export function updateElement(modelId: number, elementId: string, data: { element_name?: string; description?: string }) {
  return request.put<ModelElement>(`/models/${modelId}/elements/${elementId}`, data)
}
