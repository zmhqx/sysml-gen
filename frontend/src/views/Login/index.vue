<template>
  <div class="login-page">
    <div class="login-bg-shape shape-1" />
    <div class="login-bg-shape shape-2" />

    <div class="login-panel">
      <div class="login-brand">
        <div class="brand-logo">
          <el-icon :size="32"><Document /></el-icon>
        </div>
        <h1>SysMLDocGen</h1>
        <p>基于 SysML 模型的文档自动生成系统</p>
      </div>

      <el-card class="login-card" shadow="never">
        <h2 class="login-title">账号登录</h2>
        <el-form ref="formRef" :model="form" :rules="rules" @keyup.enter="handleLogin">
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="用户名"
              size="large"
              :prefix-icon="User"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="密码"
              size="large"
              show-password
              :prefix-icon="Lock"
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              class="login-btn"
              :loading="loading"
              @click="handleLogin"
            >
              登 录
            </el-button>
          </el-form-item>
        </el-form>
        <p class="login-hint">默认管理员：admin / admin123</p>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { Document, User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await authStore.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/home')
  } catch {
    // 错误由拦截器处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: var(--app-bg);
  position: relative;
  overflow: hidden;
}

.login-bg-shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.5;
}

.shape-1 {
  width: 400px;
  height: 400px;
  background: #c7d2fe;
  top: -100px;
  right: -80px;
}

.shape-2 {
  width: 360px;
  height: 360px;
  background: #ddd6fe;
  bottom: -80px;
  left: -60px;
}

.login-panel {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
}

.login-brand {
  text-align: center;
  margin-bottom: 28px;
}

.brand-logo {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  border-radius: 16px;
  background: linear-gradient(135deg, #4f46e5, #8b5cf6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(79, 70, 229, 0.35);
}

.login-brand h1 {
  margin: 0 0 8px;
  font-size: 26px;
  font-weight: 700;
  color: var(--app-text);
}

.login-brand p {
  margin: 0;
  font-size: 14px;
  color: var(--app-text-secondary);
}

.login-card {
  border-radius: var(--app-radius-lg) !important;
  border: 1px solid var(--app-border);
  box-shadow: var(--app-shadow) !important;
  padding: 8px 4px;
}

.login-title {
  text-align: center;
  margin: 0 0 24px;
  font-size: 18px;
  font-weight: 600;
  color: var(--app-text);
}

.login-btn {
  width: 100%;
  height: 44px;
  font-weight: 600;
  border-radius: 10px;
}

.login-hint {
  text-align: center;
  margin: 16px 0 0;
  font-size: 12px;
  color: #9ca3af;
}
</style>
