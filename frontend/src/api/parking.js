/**
 * 停车相关 API
 *
 * 对应后端端点：/api/v1/parking/
 */

import request from './request'
import axios from 'axios'

// ============================================================
// 车位 - 基础查询
// ============================================================

/** 获取车位列表（支持按楼层/区域/状态筛选） */
export function getSpots(params) {
  return request.get('/parking/spots/', { params })
}

/** 获取楼层占用率统计 */
export function getFloorSummary() {
  return request.get('/parking/spots/floor-summary/')
}

// ============================================================
// 停车位地图 (MapViewSet) - 多楼层支持
// ============================================================

/**
 * 获取特定楼层的所有停车位状态
 * @param {string} floor - 楼层代码，如 'B1', 'B2', 'B3'
 * @returns {Promise<Object>} 包含该楼层的所有停车位
 */
export function getSpacesByFloor(floor) {
  return request.get('/parking/map/spaces/', { 
    params: { floor } 
  })
}

/**
 * 获取停车场按楼层实时统计
 * @returns {Promise<Object>} 统计数据
 */
export async function getParkingSpaceStatistics() {
  const raw = await request.get('/parking/spots/floor-summary/')
  const rows = Array.isArray(raw) ? raw : (raw?.results || [])

  const normalized = rows.reduce((acc, item) => {
    const floor = item?.floor || 'B1'
    const total = Number(item?.total || 0)
    const occupied = Number(item?.occupied || 0)
    const free = Number(item?.free || 0)
    const maintenance = Number(item?.maintenance || 0)
    const reserved = Math.max(0, total - occupied - free)

    acc[floor] = {
      total,
      occupied,
      free_regular: free,
      free_charging: 0,
      reserved,
      maintenance,
    }
    return acc
  }, {})

  // HomeView 读取 res.data，此处保持兼容结构
  return { data: normalized }
}

/**
 * 查找车辆
 * @param {string} plateNumber - 车牌号
 * @param {string} floor - 楼层代码（可选）
 * @returns {Promise<Object>} 车辆位置信息
 */
export function findCarByPlate(plateNumber, floor = null) {
  const params = { plate_number: plateNumber }
  if (floor) {
    params.floor = floor
  }
  return request.get('/parking/map/find_car/', { params })
}

// ============================================================
// 停车位管理 (ParkingSpaceViewSet) - 绑定与控制
// ============================================================

/**
 * 绑定车牌到停车位
 * @param {string} spaceId - 停车位 ID
 * @param {string} plateNumber - 车牌号
 * @returns {Promise<Object>} 绑定结果
 */
export function bindPlate(spaceId, plateNumber) {
  return request.post('/parking_spaces/bind/', {
    space_id: spaceId,
    plate_number: plateNumber
  })
}

/**
 * 模拟硬件 webhook 事件
 * @param {Object} event - 事件数据
 * @returns {Promise<Object>} 处理结果
 */
export function sendWebhookEvent(event) {
  return request.post('/hardware/webhook/', event)
}

/**
 * 上传图片并识别车牌（AI）
 * @param {File} file - 图片文件
 * @param {string} scene - 场景，默认 entry
 * @returns {Promise<Object>} 识别结果
 */
export function recognizePlateFromImage(file, scene = 'entry') {
  const buildFormData = () => {
    const formData = new FormData()
    formData.append('image', file)
    formData.append('scene', scene)
    return formData
  }

  const token = localStorage.getItem('access_token')
  const headers = {
    'Content-Type': 'multipart/form-data',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }

  return axios
    .post('/api/v1/ai/recognize/', buildFormData(), { headers, timeout: 120000 })
    .then((res) => res.data)
    .catch((err) => {
      const status = Number(err?.response?.status || 0)
      if (status !== 404) {
        throw err
      }
      return axios
        .post('/api/v1/parking/ai/recognize/', buildFormData(), { headers, timeout: 30000 })
        .then((res) => res.data)
    })
}

// ============================================================
// 停车会话
// ============================================================

/** 获取当前活跃停车会话 */
export function getCurrentSessions() {
  return request.get('/parking/sessions/current/')
}

/** 获取停车会话列表 */
export function getSessions(params) {
  return request.get('/parking/sessions/', { params })
}

// ============================================================
// 预约
// ============================================================

/** 获取我的预约列表 */
export function getReservations(params) {
  return request.get('/parking/reservations/', { params })
}

/** 创建预约 */
export function createReservation(data) {
  return request.post('/parking/reservations/', data)
}

/** 取消预约 */
export function cancelReservation(id) {
  return request.post(`/parking/reservations/${id}/cancel/`)
}
