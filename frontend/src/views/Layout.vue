<template>
  <el-container class="app-shell">
    <el-aside :width="`${sidebarWidth}px`" class="app-sidebar">
      <div class="sidebar-brand">
        <div class="brand-icon">
          <el-icon :size="22"><Document /></el-icon>
        </div>
        <div class="brand-text">
          <span class="brand-name">SysMLDocGen</span>
          <span class="brand-sub">文档自动生成</span>
        </div>
      </div>

      <el-scrollbar class="sidebar-scroll">
        <el-menu
          :default-active="activeMenu"
          :default-openeds="defaultOpeneds"
          router
          class="sidebar-menu"
        >
          <div class="menu-group-label">工作台</div>
          <el-menu-item index="/home">
            <el-icon><HomeFilled /></el-icon>
            <span>首页概览</span>
          </el-menu-item>

          <div class="menu-group-label">业务模块</div>
          <el-menu-item index="/project">
            <el-icon><Folder /></el-icon>
            <span>项目管理</span>
          </el-menu-item>
          <el-menu-item index="/model">
            <el-icon><Collection /></el-icon>
            <span>模型管理</span>
          </el-menu-item>
          <el-menu-item index="/template">
            <el-icon><Memo /></el-icon>
            <span>模板管理</span>
          </el-menu-item>

          <el-sub-menu index="doc-group">
            <template #title>
              <el-icon><Files /></el-icon>
              <span>文档中心</span>
            </template>
            <el-menu-item index="/document">文档列表</el-menu-item>
            <el-menu-item index="/document/generate">生成文档</el-menu-item>
          </el-sub-menu>

          <template v-if="authStore.user?.role === 'admin'">
            <div class="menu-group-label">系统</div>
            <el-sub-menu index="admin-group">
              <template #title>
                <el-icon><Setting /></el-icon>
                <span>系统管理</span>
              </template>
              <el-menu-item index="/admin/user">用户管理</el-menu-item>
              <el-menu-item index="/admin/log">日志管理</el-menu-item>
            </el-sub-menu>
          </template>
        </el-menu>
      </el-scrollbar>

      <div class="sidebar-footer">
        <div
          class="help-card"
          role="button"
          tabindex="0"
          @click="openSwaggerDocs"
          @keyup.enter="openSwaggerDocs"
        >
          <p class="help-title">需要帮助？</p>
          <p class="help-desc">点击打开 Swagger API 文档</p>
          <span class="help-link">
            <el-icon><Link /></el-icon>
            打开 /docs
          </span>
        </div>
      </div>
    </el-aside>

    <el-container class="app-main-wrap">
      <el-header class="app-header" height="64px">
        <div class="header-left">
          <h1 class="page-title">{{ pageTitle }}</h1>
          <p class="page-subtitle">基于 SysML 模型的文档自动生成系统</p>
        </div>

        <div class="header-search-wrap">
          <el-input
            v-model="searchKeyword"
            class="header-search"
            placeholder="搜索项目、模型、文档…"
            clearable
            :prefix-icon="Search"
          />
        </div>

        <!-- 用户相关：固定顶栏最右侧 -->
        <div class="header-user-corner">
          <el-tooltip content="API 文档 (Swagger)" placement="bottom">
            <el-button class="icon-btn" circle @click="openSwaggerDocs">
              <el-icon><Document /></el-icon>
            </el-button>
          </el-tooltip>

          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-block">
              <div class="user-meta">
                <span class="user-name">{{ authStore.user?.full_name || authStore.user?.username }}</span>
                <el-tag size="small" type="info" effect="plain" class="role-tag">
                  {{ roleLabel }}
                </el-tag>
              </div>
              <el-icon class="user-arrow"><ArrowDown /></el-icon>
              <el-avatar :size="36" class="user-avatar">
                {{ userInitial }}
              </el-avatar>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>
                  {{ authStore.user?.username }}
                </el-dropdown-item>
                <el-dropdown-item command="swagger">Swagger API 文档</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="app-main">
        <div class="page-view">
          <router-view />
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import router from '../router'
import { swaggerDocsUrl } from '../api'
import {
  HomeFilled,
  Folder,
  Collection,
  Document,
  Files,
  Memo,
  Setting,
  ArrowDown,
  Search,
  Link,
} from '@element-plus/icons-vue'

const route = useRoute()
const authStore = useAuthStore()
const searchKeyword = ref('')
const sidebarWidth = 240

const defaultOpeneds = ['doc-group', 'admin-group']

const activeMenu = computed(() => {
  const p = route.path
  if (p.startsWith('/project')) return '/project'
  if (p.startsWith('/model')) return '/model'
  if (p.startsWith('/template')) return '/template'
  if (p === '/document/generate') return '/document/generate'
  if (p.startsWith('/document')) return '/document'
  if (p.startsWith('/admin/user')) return '/admin/user'
  if (p.startsWith('/admin/log')) return '/admin/log'
  return p
})

const pageTitle = computed(() => (route.meta.title as string) || '工作台')

const roleLabel = computed(() => {
  const map: Record<string, string> = {
    admin: '管理员',
    manager: '经理',
    member: '成员',
  }
  return map[authStore.user?.role || ''] || '用户'
})

const userInitial = computed(() => {
  const name = authStore.user?.full_name || authStore.user?.username || '?'
  return name.charAt(0).toUpperCase()
})

function openSwaggerDocs() {
  window.open(swaggerDocsUrl, '_blank', 'noopener,noreferrer')
}

function handleCommand(cmd: string) {
  if (cmd === 'swagger') {
    openSwaggerDocs()
    return
  }
  if (cmd === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.app-shell {
  height: 100vh;
  width: 100%;
  overflow: hidden;
  background: var(--app-bg);
}

.app-sidebar {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--app-card);
  border-right: 1px solid var(--app-border);
  box-shadow: var(--app-shadow-sm);
  flex-shrink: 0;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 16px;
  border-bottom: 1px solid var(--app-border);
}

.brand-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--app-primary), var(--app-purple));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.brand-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.brand-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--app-text);
  line-height: 1.2;
}

.brand-sub {
  font-size: 11px;
  color: var(--app-text-secondary);
  margin-top: 2px;
}

.sidebar-scroll {
  flex: 1;
}

.sidebar-menu {
  border-right: none;
  padding: 8px 10px;
  background: transparent;
}

.menu-group-label {
  font-size: 11px;
  font-weight: 600;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 16px 12px 6px;
}

.sidebar-menu :deep(.el-menu-item),
.sidebar-menu :deep(.el-sub-menu__title) {
  height: 44px;
  line-height: 44px;
  border-radius: 10px;
  margin-bottom: 2px;
  color: var(--app-text-secondary);
  font-weight: 500;
}

.sidebar-menu :deep(.el-menu-item:hover),
.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background: #f3f4f6 !important;
  color: var(--app-text);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, #eef2ff, #f5f3ff) !important;
  color: var(--app-primary) !important;
  font-weight: 600;
}

.sidebar-menu :deep(.el-menu-item.is-active::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  bottom: 8px;
  width: 3px;
  border-radius: 0 3px 3px 0;
  background: var(--app-primary);
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item) {
  padding-left: 48px !important;
  min-width: auto;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid var(--app-border);
}

.help-card {
  padding: 14px;
  border-radius: var(--app-radius);
  background: linear-gradient(135deg, #eef2ff 0%, #f5f3ff 100%);
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
  border: 1px solid transparent;
}

.help-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15);
  border-color: #c7d2fe;
}

.help-card:focus-visible {
  outline: 2px solid var(--app-primary);
  outline-offset: 2px;
}

.help-title {
  margin: 0 0 4px;
  font-size: 13px;
  font-weight: 600;
  color: var(--app-primary);
}

.help-desc {
  margin: 0 0 8px;
  font-size: 11px;
  color: var(--app-text-secondary);
  line-height: 1.4;
}

.help-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  color: var(--app-primary);
}

.app-main-wrap {
  flex: 1;
  flex-direction: column;
  min-width: 0;
  height: 100vh;
  overflow: hidden;
}

.app-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 0 20px 0 28px;
  background: var(--app-card);
  border-bottom: 1px solid var(--app-border);
  box-shadow: var(--app-shadow-sm);
  position: relative;
}

.header-left {
  flex: 0 1 auto;
  min-width: 120px;
  max-width: 280px;
}

.page-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--app-text);
  line-height: 1.3;
}

.page-subtitle {
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--app-text-secondary);
}

.header-search-wrap {
  flex: 1;
  min-width: 0;
  max-width: 520px;
}

.header-search :deep(.el-input__wrapper) {
  border-radius: 20px;
  background: #f9fafb;
  box-shadow: none;
  border: 1px solid var(--app-border);
}

/* 用户区：顶栏最右上角 */
.header-user-corner {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  margin-left: auto;
  padding-left: 16px;
}

.icon-btn {
  border: 1px solid var(--app-border);
  background: #fff;
  color: var(--app-text-secondary);
}

.user-block {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 4px 4px 4px 12px;
  border-radius: 24px;
  transition: background 0.2s;
  margin-right: -4px;
}

.user-block:hover {
  background: #f9fafb;
}

.user-avatar {
  background: linear-gradient(135deg, var(--app-primary), var(--app-purple));
  color: #fff;
  font-weight: 600;
}

.user-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
  text-align: right;
}

.user-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--app-text);
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.role-tag {
  height: 18px;
  line-height: 16px;
  padding: 0 6px;
}

.user-arrow {
  color: #9ca3af;
  font-size: 12px;
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 24px 28px !important;
  background: var(--app-bg);
  overflow: auto;
  min-height: 0;
}

@media (max-width: 1024px) {
  .header-search-wrap {
    display: none;
  }
  .page-subtitle {
    display: none;
  }
  .user-meta {
    display: none;
  }
}
</style>
