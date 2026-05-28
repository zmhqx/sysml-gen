<template>
  <div class="home-page">
    <div class="welcome-banner">
      <div class="welcome-text">
        <h2>欢迎回来，{{ displayName }}</h2>
        <p>在这里查看系统运行概况，并快速进入项目管理、模型解析与文档生成流程。</p>
      </div>
      <div class="welcome-actions">
        <el-button type="primary" size="large" @click="$router.push('/document/generate')">
          <el-icon class="btn-icon"><DocumentAdd /></el-icon>
          生成文档
        </el-button>
        <el-button size="large" @click="$router.push('/model')">上传模型</el-button>
      </div>
    </div>

    <el-row :gutter="20" class="stat-row">
      <el-col v-for="item in statItems" :key="item.key" :xs="24" :sm="12" :lg="6">
        <div class="metric-card" :class="item.theme" @click="item.route && $router.push(item.route)">
          <div class="metric-icon">
            <el-icon :size="26"><component :is="item.icon" /></el-icon>
          </div>
          <div class="metric-body">
            <div class="metric-value">{{ stats[item.key as keyof typeof stats] }}</div>
            <div class="metric-label">{{ item.label }}</div>
          </div>
          <div class="metric-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="content-row">
      <el-col :xs="24" :lg="14">
        <el-card class="panel-card">
          <template #header>
            <div class="card-header-row">
              <span>快捷操作</span>
            </div>
          </template>
          <div class="quick-grid">
            <div
              v-for="action in quickActions"
              :key="action.title"
              class="quick-item"
              @click="$router.push(action.route)"
            >
              <div class="quick-icon" :style="{ background: action.bg }">
                <el-icon :size="22" :style="{ color: action.color }">
                  <component :is="action.icon" />
                </el-icon>
              </div>
              <div class="quick-info">
                <div class="quick-title">{{ action.title }}</div>
                <div class="quick-desc">{{ action.desc }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card class="panel-card workflow-card">
          <template #header>
            <span>典型工作流</span>
          </template>
          <el-steps direction="vertical" :active="4" finish-status="success">
            <el-step title="创建或选择项目" description="在项目管理中建立工作空间" />
            <el-step title="上传并解析 SysML 模型" description="支持 XMI / XML / JSON，自动解析元素" />
            <el-step title="选择或编辑文档模板" description="Jinja2 模板驱动 HTML 文档" />
            <el-step title="生成并导出文档" description="预览后导出 Word 或 PDF" />
          </el-steps>
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
  Folder,
  Collection,
  Memo,
  Files,
  ArrowRight,
  DocumentAdd,
  Upload,
  EditPen,
  View,
} from '@element-plus/icons-vue'

const authStore = useAuthStore()

const stats = ref({
  project_count: 0,
  model_count: 0,
  template_count: 0,
  document_count: 0,
})

const displayName = computed(
  () => authStore.user?.full_name || authStore.user?.username || '用户',
)

const statItems = [
  { key: 'project_count', label: '项目数量', icon: Folder, theme: 'theme-indigo', route: '/project' },
  { key: 'model_count', label: '模型数量', icon: Collection, theme: 'theme-purple', route: '/model' },
  { key: 'template_count', label: '模板数量', icon: Memo, theme: 'theme-blue', route: '/template' },
  { key: 'document_count', label: '文档数量', icon: Files, theme: 'theme-violet', route: '/document' },
]

const quickActions = [
  {
    title: '项目管理',
    desc: '创建项目、管理成员',
    route: '/project',
    icon: Folder,
    bg: '#eef2ff',
    color: '#4f46e5',
  },
  {
    title: '上传模型',
    desc: '导入 XMI 并解析',
    route: '/model',
    icon: Upload,
    bg: '#f5f3ff',
    color: '#8b5cf6',
  },
  {
    title: '编辑模板',
    desc: '维护文档版式',
    route: '/template',
    icon: EditPen,
    bg: '#eff6ff',
    color: '#2563eb',
  },
  {
    title: '文档列表',
    desc: '预览与导出',
    route: '/document',
    icon: View,
    bg: '#fdf4ff',
    color: '#9333ea',
  },
]

onMounted(async () => {
  try {
    const res = await request.get('/admin/stats')
    stats.value = res.data
  } catch {
    // 非管理员可能无 stats 接口，保持 0
  }
})
</script>

<style scoped>
.home-page {
  width: 100%;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.welcome-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  padding: 28px 32px;
  margin-bottom: 24px;
  border-radius: var(--app-radius-lg);
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #8b5cf6 100%);
  color: #fff;
  box-shadow: 0 8px 32px rgba(79, 70, 229, 0.35);
}

.welcome-text h2 {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: 700;
}

.welcome-text p {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
  max-width: 520px;
  line-height: 1.5;
}

.welcome-actions {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

.welcome-actions .el-button--primary {
  background: #fff;
  border-color: #fff;
  color: var(--app-primary);
  font-weight: 600;
}

.welcome-actions .el-button--primary:hover {
  background: #f9fafb;
  border-color: #f9fafb;
  color: var(--app-primary-hover);
}

.welcome-actions .el-button:not(.el-button--primary) {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.4);
  color: #fff;
}

.welcome-actions .el-button:not(.el-button--primary):hover {
  background: rgba(255, 255, 255, 0.25);
}

.btn-icon {
  margin-right: 6px;
}

.stat-row {
  margin-bottom: 24px;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: var(--app-radius-lg);
  background: var(--app-card);
  box-shadow: var(--app-shadow);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid transparent;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.1);
}

.metric-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.theme-indigo .metric-icon {
  background: linear-gradient(135deg, #4f46e5, #6366f1);
}

.theme-purple .metric-icon {
  background: linear-gradient(135deg, #7c3aed, #8b5cf6);
}

.theme-blue .metric-icon {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
}

.theme-violet .metric-icon {
  background: linear-gradient(135deg, #9333ea, #a855f7);
}

.metric-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--app-text);
  line-height: 1;
}

.metric-label {
  font-size: 13px;
  color: var(--app-text-secondary);
  margin-top: 6px;
}

.metric-arrow {
  margin-left: auto;
  color: #d1d5db;
}

.metric-card:hover .metric-arrow {
  color: var(--app-primary);
}

.content-row {
  flex: 1;
}

.content-row .el-col {
  display: flex;
}

.content-row .panel-card {
  flex: 1;
  width: 100%;
  margin-bottom: 0;
}

.panel-card {
  margin-bottom: 20px;
}

.card-header-row {
  font-weight: 600;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

@media (max-width: 640px) {
  .quick-grid {
    grid-template-columns: 1fr;
  }
}

.quick-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  border-radius: var(--app-radius);
  border: 1px solid var(--app-border);
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}

.quick-item:hover {
  background: #f9fafb;
  border-color: #c7d2fe;
}

.quick-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.quick-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--app-text);
}

.quick-desc {
  font-size: 12px;
  color: var(--app-text-secondary);
  margin-top: 2px;
}

.workflow-card :deep(.el-step__title) {
  font-size: 14px;
  font-weight: 600;
}

.workflow-card :deep(.el-step__description) {
  font-size: 12px;
}
</style>
