<template>
  <el-container style="min-height: 100vh">
    <!-- 侧栏 -->
    <el-aside width="240px" class="app-sidebar">
      <div class="sidebar-logo">
        <div class="logo-icon">S</div>
        <span class="logo-text">SysMLDocGen</span>
      </div>

      <el-scrollbar>
        <el-menu
          :default-active="route.path"
          router
          class="sidebar-menu"
        >
          <el-menu-item index="/home">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/project">
            <el-icon><Folder /></el-icon>
            <span>项目管理</span>
          </el-menu-item>
          <el-menu-item index="/model">
            <el-icon><Collection /></el-icon>
            <span>模型管理</span>
          </el-menu-item>
          <el-menu-item index="/template">
            <el-icon><Document /></el-icon>
            <span>模板管理</span>
          </el-menu-item>

          <!-- 文档管理（可展开） -->
          <el-sub-menu index="/document">
            <template #title>
              <el-icon><Files /></el-icon>
              <span>文档管理</span>
            </template>
            <el-menu-item index="/document">文档列表</el-menu-item>
            <el-menu-item index="/document/generate">生成文档</el-menu-item>
          </el-sub-menu>

          <!-- 系统管理（仅 admin） -->
          <el-sub-menu index="/admin" v-if="authStore.user?.role === 'admin'">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>系统管理</span>
            </template>
            <el-menu-item index="/admin/user">用户管理</el-menu-item>
            <el-menu-item index="/admin/log">日志管理</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-scrollbar>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 顶栏 -->
      <el-header class="app-header">
        <div class="header-left">
          <h1 class="header-title">{{ pageTitle }}</h1>
        </div>
        <div class="header-right">
          <el-input
            v-model="searchQuery"
            placeholder="搜索项目、模型、文档…"
            :prefix-icon="Search"
            class="header-search"
            size="small"
            clearable
          />
          <el-divider direction="vertical" />
          <el-dropdown @command="handleCommand">
            <span class="user-link">
              <el-avatar :size="32" class="user-avatar">
                {{ userName.charAt(0).toUpperCase() }}
              </el-avatar>
              <span class="user-name">{{ userName }}</span>
              <el-tag
                v-if="authStore.user?.role"
                :type="roleTagType"
                size="small"
                effect="plain"
              >
                {{ roleLabel }}
              </el-tag>
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-item command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import router from '../router'
import {
  HomeFilled, Folder, Collection, Document,
  Files, Setting, ArrowDown, SwitchButton, Search,
} from '@element-plus/icons-vue'

const route = useRoute()
const authStore = useAuthStore()
const searchQuery = ref('')

const userName = computed(() =>
  authStore.user?.full_name || authStore.user?.username || '用户'
)

const roleLabel = computed(() => {
  const map: Record<string, string> = { admin: '管理员', manager: '经理', member: '成员' }
  return map[authStore.user?.role || ''] || authStore.user?.role || ''
})

const roleTagType = computed(() => {
  const map: Record<string, string> = { admin: 'danger', manager: 'warning', member: 'info' }
  return map[authStore.user?.role || ''] || 'info'
})

const pageTitle = computed(() => {
  const meta = route.meta?.title as string | undefined
  if (meta) return meta
  const name = route.name as string
  const map: Record<string, string> = {
    Home: '系统概览',
    ProjectList: '项目管理',
    ProjectDetail: '项目详情',
    ModelList: '模型管理',
    ModelDetail: '模型详情',
    ModelView: '模型视图',
    ModelEditor: '视图编辑器',
    TemplateList: '模板管理',
    DocumentList: '文档列表',
    DocumentGenerate: '生成文档',
    DocumentPreview: '文档预览',
    AdminUser: '用户管理',
    AdminLog: '日志管理',
  }
  return map[name] || 'SysMLDocGen'
})

function handleCommand(cmd: string) {
  if (cmd === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
/* ── 侧栏 ──────────────────── */
.app-sidebar {
  background: #fff;
  border-right: 1px solid var(--border);
  box-shadow: var(--shadow-sidebar);
  display: flex;
  flex-direction: column;
  z-index: 10;
  user-select: none;
  -webkit-user-select: none;
}
.sidebar-logo {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 10px;
  border-bottom: 1px solid var(--border);
}
.logo-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--primary), var(--accent-purple));
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 16px;
}
.logo-text {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

/* 菜单 */
.sidebar-menu {
  background: #fff;
  padding: 8px 0;
}
.sidebar-menu .el-menu-item,
.sidebar-menu .el-sub-menu__title {
  height: 44px;
  line-height: 44px;
  margin: 2px 8px;
  border-radius: 8px;
  color: var(--text-secondary);
}
.sidebar-menu .el-menu-item:hover,
.sidebar-menu .el-sub-menu__title:hover {
  background-color: var(--primary-light);
  color: var(--primary);
}
.sidebar-menu .el-menu-item.is-active {
  background-color: var(--primary-light);
  color: var(--primary);
  font-weight: 600;
}
.sidebar-menu .el-menu-item .el-icon,
.sidebar-menu .el-sub-menu__title .el-icon {
  color: inherit;
}
.sidebar-menu .el-sub-menu .el-menu-item {
  padding-left: 52px !important;
  font-size: 13px;
}

/* ── 顶栏 ──────────────────── */
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid var(--border);
  padding: 0 24px;
  height: 60px;
  user-select: none;
  -webkit-user-select: none;
}
.header-left {
  display: flex;
  align-items: center;
}
.header-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.header-search {
  width: 240px;
}
.user-link {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
.user-avatar {
  background: linear-gradient(135deg, var(--primary), var(--accent-purple));
  color: #fff;
  font-weight: 600;
}
.user-name {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

/* ── 内容区 ──────────────────── */
.app-main {
  background: var(--bg-page);
  padding: 24px;
  user-select: none;
  -webkit-user-select: none;
}
</style>
