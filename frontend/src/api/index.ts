import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

export const apiOrigin = 'http://localhost:8000'
export const swaggerDocsUrl = `${apiOrigin}/docs`
const baseURL = `${apiOrigin}/api/v1`

const request = axios.create({
  baseURL,
  timeout: 30000,
})

/** 将接口错误转为用户可读的中文提示 */
function formatErrorMessage(error: {
  response?: { status?: number; data?: { detail?: unknown } }
  message?: string
}): string {
  if (!error.response) {
    return '网络连接失败，请确认后端已启动（http://localhost:8000）'
  }
  const { status, data } = error.response
  const detail = data?.detail
  if (typeof detail === 'string') return detail
  if (status === 403) return '没有权限执行此操作'
  if (status === 404) return '请求的资源不存在'
  if (status === 500) return '服务器内部错误，请联系管理员或查看后端日志'
  if (status === 422) return '请求参数不正确'
  return error.message || '请求失败'
}

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

    const msg = formatErrorMessage(error)
    if (status !== 401 || !original?._retry) {
      ElMessage.error(msg)
    }
    return Promise.reject(error)
  },
)

export default request
