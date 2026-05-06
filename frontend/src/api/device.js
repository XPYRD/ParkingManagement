/**
 * 设备管理 API
 *
 * 对应后端端点：/api/v1/devices/
 */

import request from './request'

/** 获取设备列表 */
export function getDevices(params) {
  return request.get('/devices/list/', { params })
}

/** 获取设备详情 */
export function getDevice(id) {
  return request.get(`/devices/list/${id}/`)
}

/** 获取设备概览统计 */
export function getDeviceOverview() {
  return request.get('/devices/list/overview/')
}

/** 更新设备 */
export function updateDevice(id, data) {
  return request.put(`/devices/list/${id}/`, data)
}

/** 报告设备故障 */
export function reportFault(id, faultDetail) {
  return request.post(`/devices/list/${id}/report-fault/`, {
    fault_detail: faultDetail,
  })
}

/** 重启设备 */
export function restartDevice(id, type = 'soft') {
  return request.post(`/devices/list/${id}/restart/`, { type })
}
