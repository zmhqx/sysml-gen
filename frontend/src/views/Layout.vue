<template>
  <el-container style="min-height: 100vh">
    <el-aside width="220px" class="app-sidebar">
      <div class="sidebar-title">SysMLDocGen</div>
      <el-menu
        :default-active="route.path"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
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
        <el-menu-item index="/document">
          <el-icon><Files /></el-icon>
          <span>文档管理</span>
        </el-menu-item>
        <el-sub-menu index="/admin" v-if="authStore.user?.role === 'admin'">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/admin/user">用户管理</el-menu-item>
          <el-menu-item index="/admin/log">日志管理</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="app-header">
        <div class="header-title">基于SysML模型的文档自动生成系统</div>
        <div class="header-user">
          <el-dropdown @command="handleCommand">
            <span class="user-link">
              {{ authStore.user?.full_name || authStore.user?.username }}
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import router from '../router'
import {
  HomeFilled, Folder, Collection, Document,
  Files, Setting, ArrowDown,
} from '@element-plus/icons-vue'

const route = useRoute()
const authStore = useAuthStore()

function handleCommand(cmd: string) {
  if (cmd === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.app-sidebar {
  background-color: #304156;
}
.sidebar-title {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid #1f2d3d;
}
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 20px;
}
.header-title {
  font-size: 16px;
  font-weight: 600;
}
.user-link {
  cursor: pointer;
  color: #409EFF;
}
</style>
