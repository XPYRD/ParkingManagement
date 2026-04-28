/**
 * 认证相关 API
 *
 * 对应后端端点：/api/v1/auth/
 */

import request from './request'

/**
 * 用户登录 — 获取 JWT Token
 * @param {Object} data - { username, password }
 * @returns {Promise<{access: string, refresh: string}>}
 */
export function login(data) {
  return request.post('/auth/token/', data)
}

/**
 * 刷新 JWT Token
 * @param {string} refresh - refresh token
 * @returns {Promise<{access: string}>}
 */
export function refreshToken(refresh) {
  return request.post('/auth/token/refresh/', { refresh })
}
