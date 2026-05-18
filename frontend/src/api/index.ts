import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const baseURL = 'http://localhost:8000/api/v1'

const request = axios.create({
  baseURL,
  timeout: 30000,
})

let isRefreshing = false

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config as typeof error.config & { _retry?: boolean }
    const status = error.response?.status

    // 对于 blob 响应，错误信息需要特殊解析
    if (original?.responseType === 'blob' && error.response?.data instanceof Blob) {
      try {
        const text = await error.response.data.text()
        const json = JSON.parse(text)
        ElMessage.error(json.detail || '下载失败')
      } catch {
        ElMessage.error('下载失败')
      }
      return Promise.reject(error)
    }

    if (
      status === 401 &&
      original &&
      !original._retry &&
      !original.url?.includes('/auth/login') &&
      !original.url?.includes('/auth/refresh')
    ) {
      const refresh = localStorage.getItem('refresh_token')
      if (refresh && !isRefreshing) {
        isRefreshing = true
        original._retry = true
        try {
          const { data } = await axios.post<{ access_token: string; refresh_token: string }>(
            `${baseURL}/auth/refresh`,
            { refresh_token: refresh },
          )
          localStorage.setItem('token', data.access_token)
          localStorage.setItem('refresh_token', data.refresh_token)
          original.headers = original.headers || {}
          original.headers.Authorization = `Bearer ${data.access_token}`
          isRefreshing = false
          return request(original)
        } catch {
          isRefreshing = false
        }
      }
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      router.push('/login')
    }

    const msg = error.response?.data?.detail || error.message || 'Request failed'
    if (status !== 401 || !original?._retry) {
      ElMessage.error(typeof msg === 'string' ? msg : JSON.stringify(msg))
    }
    return Promise.reject(error)
  },
)

export default request
