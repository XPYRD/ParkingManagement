/**
 * 预警与工单 API
 *
 * 对应后端端点：/api/v1/alerts/
 */

import request from './request'

// ============================================================
// 系统预警
// ============================================================

/** [管理端] 获取告警列表 */
export function getAlerts(params) {
  return request.get('/alerts/alerts/', { params })
}

/** [管理端] 获取告警统计 */
export function getAlertStats() {
  return request.get('/alerts/alerts/stats/')
}

/** [管理端] 标记告警已解决 */
export function resolveAlert(id) {
  return request.post(`/alerts/alerts/${id}/resolve/`)
}

// ============================================================
// 用户工单
// ============================================================

/** 获取我的工单列表 */
export function getTickets(params) {
  return request.get('/alerts/tickets/', { params })
}

/** 提交工单 */
export function createTicket(data) {
  return request.post('/alerts/tickets/', data)
}
