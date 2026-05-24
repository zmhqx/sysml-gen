<template>
  <div class="home-page">
    <!-- 统计指标卡 -->
    <el-row :gutter="20">
      <el-col :span="6" v-for="item in metrics" :key="item.label">
        <el-card shadow="never" class="metric-card">
          <div class="metric-inner">
            <div class="metric-icon" :style="{ background: item.bg }">
              <el-icon :size="22"><component :is="item.icon" /></el-icon>
            </div>
            <div class="metric-body">
              <div class="metric-value">{{ item.count }}</div>
              <div class="metric-label">{{ item.label }}</div>
            </div>
          </div>
          <div class="metric-trend" v-if="item.trend !== undefined">
            <span :class="item.trend >= 0 ? 'trend-up' : 'trend-down'">
              {{ item.trend >= 0 ? '+' : '' }}{{ item.trend }}%
            </span>
            <span class="trend-period">较上月</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表 + 快捷操作 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>近 30 天文档生成量</span>
            </div>
          </template>
          <div class="chart-placeholder">
            <div class="chart-bars">
              <div
                v-for="(v, i) in chartData"
                :key="i"
                class="chart-bar-item"
              >
                <div
                  class="chart-bar"
                  :style="{ height: (v / maxChart) * 160 + 'px' }"
                ></div>
                <div class="chart-label">{{ i + 1 }}日</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button
              type="primary"
              class="action-btn"
              @click="$router.push('/project')"
            >
              <el-icon><Folder /></el-icon>
              项目管理
            </el-button>
            <el-button
              class="action-btn"
              @click="$router.push('/model')"
            >
              <el-icon><Collection /></el-icon>
              模型管理
            </el-button>
            <el-button
              type="success"
              class="action-btn"
              @click="$router.push('/document/generate')"
            >
              <el-icon><Files /></el-icon>
              生成文档
            </el-button>
            <el-button
              class="action-btn"
              @click="$router.push('/template')"
            >
              <el-icon><Document /></el-icon>
              模板管理
            </el-button>
          </div>
        </el-card>

        <!-- 系统信息 -->
        <el-card shadow="never" style="margin-top: 16px">
          <template #header>
            <div class="card-header">
              <span>系统信息</span>
            </div>
          </template>
          <div class="sys-info">
            <div class="info-row">
              <span class="info-label">登录用户</span>
              <span class="info-value">
                {{ authStore.user?.full_name || authStore.user?.username }}
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">角色</span>
              <span class="info-value">
                <el-tag :type="roleTagType" size="small" effect="plain">
                  {{ roleLabel }}
                </el-tag>
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">系统版本</span>
              <span class="info-value">v1.0.0</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import request from '../../api'
import {
  Folder, Collection, Document, Files, Tickets, DataAnalysis, EditPen, ChatDotSquare,
} from '@element-plus/icons-vue'
import type { Component } from 'vue'

const authStore = useAuthStore()

const stats = ref({
  project_count: 0,
  model_count: 0,
  template_count: 0,
  document_count: 0,
})

const chartData = ref<number[]>([])

interface MetricItem {
  label: string
  count: number
  icon: Component
  bg: string
  trend?: number
}

const metrics = computed<MetricItem[]>(() => [
  { label: '项目数量', count: stats.value.project_count, icon: Folder, bg: '#eef2ff', trend: 12 },
  { label: '模型数量', count: stats.value.model_count, icon: DataAnalysis, bg: '#f0fdf4', trend: 8 },
  { label: '模板数量', count: stats.value.template_count, icon: EditPen, bg: '#fefce8', trend: -3 },
  { label: '文档数量', count: stats.value.document_count, icon: Tickets, bg: '#fdf2ff', trend: 25 },
])

const maxChart = computed(() => Math.max(...chartData.value, 1))

const roleLabel = computed(() => {
  const map: Record<string, string> = { admin: '管理员', manager: '经理', member: '成员' }
  return map[authStore.user?.role || ''] || ''
})
const roleTagType = computed(() => {
  const map: Record<string, string> = { admin: 'danger', manager: 'warning', member: 'info' }
  return map[authStore.user?.role || ''] || 'info'
})

onMounted(async () => {
  try {
    const res = await request.get('/admin/stats')
    stats.value = res.data
  } catch { /* ok */ }

  // 模拟近 30 天文档生成趋势
  chartData.value = Array.from({ length: 30 }, () =>
    Math.floor(Math.random() * 8) + 1
  )
})
</script>

<style scoped>
/* 首页容器防文本光标 */
.home-page {
  user-select: none;
  -webkit-user-select: none;
}
/* 指标卡 */
.metric-card {
  transition: transform 0.2s, box-shadow 0.2s;
}
.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.1) !important;
}
.metric-inner {
  display: flex;
  align-items: center;
  gap: 16px;
}
.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
  flex-shrink: 0;
}
.metric-body {
  flex: 1;
}
.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}
.metric-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 2px;
}
.metric-trend {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--border);
  font-size: 12px;
}
.trend-up { color: var(--status-success); font-weight: 600; }
.trend-down { color: var(--status-danger); font-weight: 600; }
.trend-period { color: var(--text-muted); margin-left: 4px; }

/* 图表 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 15px;
}
.chart-placeholder {
  height: 200px;
  display: flex;
  align-items: flex-end;
}
.chart-bars {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  width: 100%;
  height: 100%;
}
.chart-bar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  justify-content: flex-end;
}
.chart-bar {
  width: 100%;
  max-width: 24px;
  background: linear-gradient(180deg, var(--primary), var(--accent-purple));
  border-radius: 4px 4px 0 0;
  min-height: 4px;
  transition: height 0.4s ease;
}
.chart-label {
  font-size: 10px;
  color: var(--text-muted);
  margin-top: 4px;
}

/* 快捷操作 */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.action-btn {
  width: 100%;
  justify-content: flex-start;
  padding: 12px 16px;
  height: auto;
}

/* 系统信息 */
.sys-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.info-label {
  color: var(--text-secondary);
  font-size: 13px;
}
.info-value {
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 500;
}
</style>
