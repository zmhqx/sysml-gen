import request from './index'
import type { Document, DocumentListResponse } from '../types'

export function getDocuments(params: {
  project_id?: number
  page?: number
  page_size?: number
}) {
  return request.get<DocumentListResponse>('/documents', { params })
}

export function getDocument(id: number) {
  return request.get<Document>(`/documents/${id}`)
}

export function generateDocument(data: {
  project_id: number
  model_id: number
  template_id: number
}) {
  return request.post<Document>('/documents/generate', data)
}

export function previewDocument(id: number) {
  return request.get<{ content: string; document_name: string }>(
    `/documents/${id}/preview`,
  )
}

export function downloadDocument(id: number, fmt: string) {
  const isHtml = fmt === 'html'
  return request.get(`/documents/${id}/download`, {
    params: { fmt },
    responseType: isHtml ? 'json' : 'blob',
  })
}

export function deleteDocument(id: number) {
  return request.delete(`/documents/${id}`)
}
