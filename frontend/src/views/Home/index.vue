<template>
  <div class="home-page">
    <h2>系统概览</h2>
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ stats.project_count }}</div>
            <div class="stat-label">项目数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ stats.model_count }}</div>
            <div class="stat-label">模型数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ stats.template_count }}</div>
            <div class="stat-label">模板数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-value">{{ stats.document_count }}</div>
            <div class="stat-label">文档数量</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 20px">
      <template #header>快捷操作</template>
      <el-button type="primary" @click="$router.push('/project')">项目管理</el-button>
      <el-button type="success" @click="$router.push('/document/generate')">生成文档</el-button>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '../../api'

const stats = ref({
  project_count: 0,
  model_count: 0,
  template_count: 0,
  document_count: 0,
})

onMounted(async () => {
  try {
    const res = await request.get('/admin/stats')
    stats.value = res.data
  } catch {
    // Non-admin users may not have access
  }
})
</script>

<style scoped>
.stat-card {
  text-align: center;
  padding: 10px 0;
}
.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #409EFF;
}
.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}
</style>
