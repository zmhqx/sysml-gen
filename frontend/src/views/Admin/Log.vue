<template>
  <div>
    <div class="page-header">
      <h2>日志管理</h2>
    </div>

    <el-card style="margin-bottom: 16px">
      <el-form :inline="true" :model="filters">
        <el-form-item label="日志类型">
          <el-select v-model="filters.log_type" placeholder="全部" clearable style="width: 140px">
            <el-option label="登录" value="login" />
            <el-option label="操作" value="operation" />
            <el-option label="错误" value="error" />
            <el-option label="系统" value="system" />
          </el-select>
        </el-form-item>
        <el-form-item label="模块">
          <el-select v-model="filters.module_name" placeholder="全部" clearable style="width: 140px">
            <el-option label="项目" value="project" />
            <el-option label="模型" value="model" />
            <el-option label="模板" value="template" />
            <el-option label="文档" value="document" />
            <el-option label="用户" value="user" />
            <el-option label="认证" value="auth" />
          </el-select>
        </el-form-item>
        <el-form-item label="结果">
          <el-select v-model="filters.result_status" placeholder="全部" clearable style="width: 140px">
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failed" />
            <el-option label="警告" value="warning" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-table :data="logs" border stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="log_type" label="类型" width="80">
        <template #default="{ row }">
          <el-tag :type="logTypeTag(row.log_type)" size="small">
            {{ logTypeLabel(row.log_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="module_name" label="模块" width="80" />
      <el-table-column prop="operation_content" label="操作内容" min-width="350" show-overflow-tooltip />
      <el-table-column prop="result_status" label="结果" width="80">
        <template #default="{ row }">
          <el-tag
            :type="row.result_status === 'success' ? 'success' : row.result_status === 'failed' ? 'danger' : 'warning'"
            size="small"
          >
            {{ { success: '成功', failed: '失败', warning: '警告' }[row.result_status] || row.result_status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="ip_address" label="IP" width="140" />
      <el-table-column prop="record_time" label="时间" width="180" />
    </el-table>

    <div style="display: flex; justify-content: center; margin-top: 20px">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchLogs"
        @current-change="fetchLogs"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getAdminLogs } from '../../api/admin'
import type { LogOut } from '../../types'

const logs = ref<LogOut[]>([])
const loading = ref(false)
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0,
})
const filters = reactive({
  log_type: undefined as string | undefined,
  module_name: undefined as string | undefined,
  result_status: undefined as string | undefined,
})

function logTypeTag(type: string) {
  const m: Record<string, string> = {
    login: 'primary',
    operation: '',
    error: 'danger',
    system: 'warning',
  }
  return m[type] || 'info'
}

function logTypeLabel(type: string) {
  const m: Record<string, string> = {
    login: '登录',
    operation: '操作',
    error: '错误',
    system: '系统',
  }
  return m[type] || type
}

async function fetchLogs() {
  loading.value = true
  try {
    const res = await getAdminLogs({
      ...filters,
      page: pagination.page,
      page_size: pagination.page_size,
    })
    logs.value = res.data.items
    pagination.total = res.data.total
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchLogs()
}

function handleReset() {
  filters.log_type = undefined
  filters.module_name = undefined
  filters.result_status = undefined
  pagination.page = 1
  fetchLogs()
}

onMounted(fetchLogs)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>
