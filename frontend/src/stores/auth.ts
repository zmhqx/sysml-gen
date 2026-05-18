import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, getMe } from '../api/auth'
import type { User } from '../types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref(localStorage.getItem('token') || '')
  const isLoggedIn = ref(!!token.value)

  /**
   * @param refreshToken 传入字符串则写入 localStorage；登出时传 undefined 并清空 access
   */
  function setSession(accessToken: string, newUser: User | null, refreshToken?: string) {
    token.value = accessToken
    user.value = newUser
    if (accessToken) {
      localStorage.setItem('token', accessToken)
      isLoggedIn.value = true
      if (typeof refreshToken === 'string' && refreshToken) {
        localStorage.setItem('refresh_token', refreshToken)
      }
    } else {
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      isLoggedIn.value = false
    }
  }

  async function login(username: string, password: string) {
    const res = await loginApi(username, password)
    setSession(res.data.access_token, null, res.data.refresh_token)
    await fetchUser()
  }

  async function fetchUser() {
    try {
      const res = await getMe()
      user.value = res.data
    } catch {
      logout()
    }
  }

  function logout() {
    setSession('', null)
  }

  return { user, token, isLoggedIn, setSession, login, fetchUser, logout }
})
