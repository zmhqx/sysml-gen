<template>
  <router-view v-if="authReady" />
  <div v-else style="display:flex;justify-content:center;align-items:center;height:100vh;color:#909399;font-size:16px">
    加载中...
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import router from './router'

const authStore = useAuthStore()
const authReady = ref(false)

onMounted(async () => {
  if (authStore.token) {
    await authStore.fetchUser()
    if (!authStore.token) {
      router.replace('/login')
    }
  }
  authReady.value = true
})
</script>
