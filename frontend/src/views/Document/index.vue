<template>
  <div>
    <div class="page-header">
      <h2>文档管理</h2>
      <div>
        <el-select
          v-model="filterProjectId"
          placeholder="按项目筛选"
          clearable
          style="width: 200px; margin-right: 12px"
          @change="handleFilterChange"
        >
          <el-option
            v-for="p in projectStore.projects"
            :key="p.id"
            :label="p.name"
            :value="p.id"
          />
        </el-select>
        <el-button type="primary" @click="$router.push('/document/generate')">生成文档</el-button>
      </div>
    </div>

    <el-table :data="documents" border stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="document_name" label="文档名称" min-width="200">
        <template #default="{ row }">
          <router-link :to="`/document/${row.id}`">{{ row.document_name }}</router-link>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" size="small">
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="generate_time" label="生成时间" width="180" />
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push(`/document/${row.id}`)">预览</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div style="display: flex; justify-content: center; margin-top: 20px">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :page-sizes="[10, 20, 50]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchDocuments"
        @current-change="fetchDocuments"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useProjectStore } from '../../stores/project'
import { getDocuments, deleteDocument } from '../../api/document'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Document } from '../../types'

const projectStore = useProjectStore()
const documents = ref<Document[]>([])
const loading = ref(false)
const filterProjectId = ref<number | undefined>(undefined)

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0,
})

function statusType(status: string) {
  return { generating: 'warning', success: 'success', failed: 'danger' }[status] || 'info'
}

function statusLabel(status: string) {
  return { generating: '生成中', success: '已生成', failed: '失败' }[status] || status
}

function handleFilterChange() {
  pagination.page = 1
  fetchDocuments()
}

async function fetchDocuments() {
  loading.value = true
  try {
    const res = await getDocuments({
      project_id: filterProjectId.value || undefined,
      page: pagination.page,
      page_size: pagination.page_size,
    })
    documents.value = res.data.items
    pagination.total = res.data.total
  } finally {
    loading.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定删除该文档？')
    await deleteDocument(id)
    ElMessage.success('文档已删除')
    await fetchDocuments()
  } catch {
    // cancelled
  }
}

onMounted(async () => {
  await projectStore.fetchAll()
  await fetchDocuments()
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>
