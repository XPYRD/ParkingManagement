/**
 * 认证状态管理
 *
 * 管理 JWT Token 和用户信息
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi } from '@/api/auth'
import { getProfile as getProfileApi } from '@/api/user'

export const useAuthStore = defineStore('auth', () => {
  // ---- 状态 ----
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('user_info') || 'null'))

  // ---- 计算属性 ----
  const isLoggedIn = computed(() => !!accessToken.value)

  // ---- 操作 ----

  /**
   * 用户登录
   * @param {Object} credentials - { username, password }
   */
  async function login(credentials) {
    try {
      const data = await loginApi(credentials)
      
      // 如果需要两步验证，直接返回数据由视图处理，不保存 token
      if (data.requires_2fa) {
        return data
      }

      accessToken.value = data.access
      refreshToken.value = data.refresh
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      
      // 获取并保存用户信息
      const profile = await getProfileApi()
      userInfo.value = profile
      localStorage.setItem('user_info', JSON.stringify(profile))
      
      return data
    } catch (error) {
      throw error
    }
  }

  /**
   * 两步验证核验
   * @param {Object} data - { username, password, code }
   */
  async function verify2FA(data) {
    try {
      const response = await request.post('/auth/token/verify-2fa/', data)
      accessToken.value = response.access
      refreshToken.value = response.refresh
      localStorage.setItem('access_token', response.access)
      localStorage.setItem('refresh_token', response.refresh)

      // 获取并保存用户信息
      const profile = await getProfileApi()
      userInfo.value = profile
      localStorage.setItem('user_info', JSON.stringify(profile))
      
      return response
    } catch (error) {
      throw error
    }
  }

  /** 退出登录 — 清除所有凭据 */
  function logout() {
    accessToken.value = ''
    refreshToken.value = ''
    userInfo.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_info')
  }

  return {
    accessToken,
    refreshToken,
    userInfo,
    isLoggedIn,
    login,
    logout,
    verify2FA,
  }
})
