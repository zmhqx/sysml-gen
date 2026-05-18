<template>
  <div v-if="project">
    <h2>{{ project.name }}</h2>
    <p style="color: #909399; margin: 8px 0">{{ project.description }}</p>
    <p style="font-size: 13px; color: #c0c4cc">创建时间: {{ project.created_at }}</p>

    <h3 style="margin-top: 24px">关联模型</h3>
    <el-button type="primary" size="small" @click="$router.push('/model')">查看所有模型</el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getProject } from '../../api/project'
import type { Project } from '../../types'

const route = useRoute()
const project = ref<Project | null>(null)

onMounted(async () => {
  const res = await getProject(Number(route.params.id))
  project.value = res.data
})
</script>
