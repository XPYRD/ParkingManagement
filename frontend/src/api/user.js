/**
 * 用户与车辆管理 API
 *
 * 对应后端端点：/api/v1/accounts/
 */

import request from './request'

// ============================================================
// 注册 & 个人信息
// ============================================================

/** 用户注册 */
export function register(data) {
  return request.post('/accounts/register/', data)
}

/** 获取当前用户信息 */
export function getProfile() {
  return request.get('/accounts/profile/')
}

/** 更新个人信息 */
export function updateProfile(data) {
  return request.put('/accounts/profile/', data)
}

/** 修改密码 */
export function changePassword(data) {
  return request.post('/accounts/change-password/', data)
}

// ============================================================
// 车辆管理
// ============================================================

/** 获取我的车辆列表 */
export function getVehicles() {
  return request.get('/accounts/vehicles/')
}

/** 添加车辆 */
export function addVehicle(data) {
  return request.post('/accounts/vehicles/', data)
}

/** 更新车辆 */
export function updateVehicle(id, data) {
  return request.put(`/accounts/vehicles/${id}/`, data)
}

/** 删除车辆 */
export function deleteVehicle(id) {
  return request.delete(`/accounts/vehicles/${id}/`)
}

/** 设为默认车辆 */
export function setPrimaryVehicle(id) {
  return request.post(`/accounts/vehicles/${id}/set-primary/`)
}

// ============================================================
// [管理端] 用户管理
// ============================================================

/** [管理端] 获取用户列表 */
export function getUsers(params) {
  return request.get('/accounts/admin/users/', { params })
}

/** [管理端] 封禁/解封用户 */
export function toggleUserBan(id) {
  return request.post(`/accounts/admin/users/${id}/toggle-ban/`)
}
