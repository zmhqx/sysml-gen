import request from './index'
import type { Project, ProjectMember } from '../types'

export function getProjects() {
  return request.get<Project[]>('/projects')
}

export function getProject(id: number) {
  return request.get<Project>(`/projects/${id}`)
}

export function createProject(data: { name: string; description?: string }) {
  return request.post<Project>('/projects', data)
}

export function updateProject(id: number, data: Partial<Project>) {
  return request.put<Project>(`/projects/${id}`, data)
}

export function deleteProject(id: number) {
  return request.delete(`/projects/${id}`)
}

export function getProjectMembers(projectId: number) {
  return request.get<ProjectMember[]>(`/projects/${projectId}/members`)
}

export function addProjectMember(projectId: number, userId: number) {
  return request.post<ProjectMember>(`/projects/${projectId}/members`, { user_id: userId })
}

export function removeProjectMember(projectId: number, userId: number) {
  return request.delete(`/projects/${projectId}/members/${userId}`)
}
