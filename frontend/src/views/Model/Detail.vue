<template>
  <div v-loading="loading">
    <div v-if="model">
      <el-page-header @back="$router.push('/model')" content="模型详情" />

      <el-card style="margin-top: 20px">
        <template #header>基本信息</template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="模型名称">{{ model.name }}</el-descriptions-item>
          <el-descriptions-item label="版本号">{{ model.version_tag }}</el-descriptions-item>
          <el-descriptions-item label="所属项目">{{ projectName }}</el-descriptions-item>
          <el-descriptions-item label="文件类型">{{ model.file_type }}</el-descriptions-item>
          <el-descriptions-item label="文件大小">{{ formatSize(model.file_size) }}</el-descriptions-item>
          <el-descriptions-item label="解析状态">
            <el-tag :type="statusType(model.parse_status)" size="small">
              {{ statusLabel(model.parse_status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="上传时间">{{ model.upload_time || '—' }}</el-descriptions-item>
          <el-descriptions-item label="解析信息">{{ model.parse_message || '—' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-card style="margin-top: 20px">
        <template #header>
          <span>模型元素（{{ elements.length }}）</span>
          <el-button size="small" style="margin-left: 12px" @click="$router.push(`/model/${model.id}/view`)">查看元素树</el-button>
          <el-button size="small" type="success" style="margin-left: 8px" @click="$router.push(`/model/${model.id}/editor`)">视图编辑器</el-button>
        </template>
        <el-table :data="elements" border stripe style="width: 100%" max-height="400">
          <el-table-column prop="element_id" label="ID" width="100" />
          <el-table-column prop="element_name" label="名称" min-width="200" />
          <el-table-column prop="element_type" label="类型" width="140">
            <template #default="{ row }">
              <el-tag :type="elementTypeTag(row.element_type)" size="small">{{ row.element_type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="300" show-overflow-tooltip />
        </el-table>
      </el-card>
    </div>
    <el-empty v-else description="模型不存在" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectStore } from '../../stores/project'
import { getModel, getModelElements } from '../../api/model'
import type { SysModel, ModelElement } from '../../types'

const route = useRoute()
const projectStore = useProjectStore()
const model = ref<SysModel | null>(null)
const elements = ref<ModelElement[]>([])
const loading = ref(true)

const projectName = computed(() => {
  if (!model.value) return '—'
  const p = projectStore.projects.find((p) => p.id === model.value!.project_id)
  return p?.name || '—'
})

function formatSize(bytes: number) {
  if (!bytes) return '—'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function statusType(status: string) {
  return { pending: 'info', parsing: 'warning', success: 'success', failed: 'danger' }[status] || 'info'
}

function statusLabel(status: string) {
  return { pending: '待解析', parsing: '解析中', success: '已解析', failed: '解析失败' }[status] || status
}

function elementTypeTag(type: string) {
  const colors: Record<string, string> = {
    Block: 'primary', Requirement: 'warning', Package: '',
    Interface: 'success', Association: 'info',
  }
  return colors[type] || ''
}

onMounted(async () => {
  try {
    const id = Number(route.params.id)
    await projectStore.fetchAll()
    const [modelRes, elementsRes] = await Promise.all([
      getModel(id),
      getModelElements(id),
    ])
    model.value = modelRes.data
    elements.value = elementsRes.data
  } finally {
    loading.value = false
  }
})
</script>
