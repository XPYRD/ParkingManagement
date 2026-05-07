/**
 * Axios 请求封装
 *
 * 统一拦截器：
 * - 请求拦截：自动附加 JWT Token
 * - 响应拦截：401 跳转登录，统一错误提示
 */

import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  // Vite 环境变量（VITE_API_URL）或兼容的 VUE_APP_API_URL；若未配置则回退到相对路径
  baseURL: (import.meta.env.VITE_API_URL || import.meta.env.VUE_APP_API_URL)
    ? `${(import.meta.env.VITE_API_URL || import.meta.env.VUE_APP_API_URL).replace(/\/+$/, '')}/api/v1`
    : '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 — 附加 JWT Token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器 — 统一错误处理
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const status = error.response?.status
    const data = error.response?.data

    if (status === 401) {
      // 登录失败或 Token 无效
      const detail = data?.detail || error.message
      
      // 翻译常见的 SimpleJWT 错误信息
      let displayMsg = detail
      if (detail.includes('No active account found')) {
        displayMsg = '账号或密码错误'
      } else if (detail.includes('User is inactive')) {
        displayMsg = '账号已被锁定或未激活'
      }

      // 如果当前不在登录页面，说明是凭据过期，静默跳转
      if (window.location.pathname !== '/login' && window.location.pathname !== '/admin/login') {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      } else {
        // 在登录页触发的 401 必须提示用户
        ElMessage.error(displayMsg)
      }
    } else if (status === 403) {
      ElMessage.error('权限不足，请联系管理员')
    } else if (status >= 500) {
      ElMessage.error('服务器异常，请稍后重试')
    } else if (!error.config?.__suppressToast) {
      // 尝试提取后端返回的详细错误信息
      const detail = data?.detail || error.message
      ElMessage.error(detail)
    }

    return Promise.reject(error)
  }
)

// 公共请求函数：用于免登录的接口，自动标记 skipAuthRedirect
export const publicRequest = (config) => request({ ...config, skipAuthRedirect: true })

export default request
