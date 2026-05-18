import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getProjects, createProject as createApi, updateProject as updateApi, deleteProject as deleteApi } from '../api/project'
import type { Project } from '../types'

export const useProjectStore = defineStore('project', () => {
  const projects = ref<Project[]>([])

  async function fetchAll() {
    const res = await getProjects()
    projects.value = res.data
  }

  async function create(data: { name: string; description?: string }) {
    const res = await createApi(data)
    projects.value.unshift(res.data)
    return res.data
  }

  async function update(id: number, data: Partial<Project>) {
    const res = await updateApi(id, data)
    const idx = projects.value.findIndex((p) => p.id === id)
    if (idx !== -1) projects.value[idx] = res.data
    return res.data
  }

  async function remove(id: number) {
    await deleteApi(id)
    projects.value = projects.value.filter((p) => p.id !== id)
  }

  return { projects, fetchAll, create, update, remove }
})
