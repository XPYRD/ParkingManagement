/**
 * 停车位地图与反向寻车 API 服务
 * 
 * 模块职责：
 * 1. 地图初始化 - 获取所有车位状态
 * 2. 寻车功能 - 根据车牌号查询车位位置
 * 3. 硬件 WebHook - 推送车位状态变更事件
 * 4. 路径规划 - 计算导航路径
 */

import axios from 'axios'

const API_BASE = '/api/v1'

// ========== 地图数据接口 ==========

/**
 * 获取全局车位状态
 * 
 * 对应 PRD Section 6.1
 * 
 * @returns {Promise<{code: number, data: Array<{space_id: string, status: number}>}>}
 */
export async function getMapSpaces() {
  try {
    const response = await axios.get(`${API_BASE}/map/spaces/`)
    return response.data
  } catch (error) {
    console.error('获取地图车位数据失败:', error)
    throw error
  }
}

/**
 * 根据车牌号寻车
 * 
 * 对应 PRD Section 6.2
 * 
 * @param {string} plateNumber - 车牌号，如 "京A88888"
 * @returns {Promise<{code: number, data: {plate_number: string, space_id: string, location_desc: string}}>}
 */
export async function findCarByPlate(plateNumber) {
  try {
    const response = await axios.get(`${API_BASE}/map/find_car/`, {
      params: { plate_number: plateNumber }
    })
    return response.data
  } catch (error) {
    console.error('寻车失败:', error)
    throw error
  }
}

// ========== 硬件 WebHook 接口 ==========

/**
 * 发送车位状态变更事件
 * 
 * 对应 PRD Section 3.3 (Backend Specifications)
 * 
 * @param {Object} event - 事件对象
 * @param {string} event.event_type - 事件类型 (space_occupied | space_released | space_maintenance)
 * @param {string} event.space_id - 车位 ID，如 "space_A001"
 * @param {string} [event.plate_number] - 车牌号（占用时提供）
 * @param {string} [event.timestamp] - 时间戳，ISO 8601 格式
 * 
 * @returns {Promise<{code: number, message: string, space_id: string, status: number}>}
 */
export async function pushSpaceStatusEvent(event) {
  try {
    const response = await axios.post(`${API_BASE}/hardware/webhook/`, event)
    return response.data
  } catch (error) {
    console.error('推送车位事件失败:', error)
    throw error
  }
}

// ========== 路径规划接口 ==========

/**
 * 计算两个停车位间的最短导航路径
 * 
 * 对应 PRD Section 4.2 & 6 (Navigation Module)
 * 
 * @param {number} startSpotId - 起点车位 ID
 * @param {number} endSpotId - 终点车位 ID
 * @returns {Promise<{path: Array, distance: number, steps: Array}>}
 */
export async function calculateNavigationPath(startSpotId, endSpotId) {
  try {
    const response = await axios.post(`${API_BASE}/parking/navigation/find-path/`, {
      start_spot_id: startSpotId,
      end_spot_id: endSpotId
    })
    return response.data
  } catch (error) {
    console.error('计算导航路径失败:', error)
    throw error
  }
}

// ========== 实时 WebSocket 连接（可选，用于实时更新）==========

/**
 * WebSocket 实时车位状态更新
 * 
 * 用途：实时推送车位状态变更，而不需要轮询
 * 
 * @param {Function} onStatusChange - 状态变更回调函数
 * @param {Function} [onError] - 错误回调函数
 * @returns {WebSocket} WebSocket 连接对象
 */
export function subscribeToSpaceUpdates(onStatusChange, onError) {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${window.location.host}/ws/parking/spaces/`
  
  const ws = new WebSocket(wsUrl)
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      onStatusChange(data)
    } catch (error) {
      console.error('解析 WebSocket 消息失败:', error)
    }
  }
  
  ws.onerror = (error) => {
    console.error('WebSocket 错误:', error)
    if (onError) onError(error)
  }
  
  ws.onclose = () => {
    console.log('WebSocket 连接已关闭')
  }
  
  return ws
}

// ========== 高级工具函数 ==========

/**
 * 监听单个车位的状态变更
 * 
 * 用于需要持续监听某个特定车位状态的场景
 * 
 * @param {string} spaceId - 车位 ID
 * @param {Function} onStatusChange - 状态变更回调
 * @param {number} [pollInterval=3000] - 轮询间隔（毫秒）
 * @returns {number} 轮询 ID，可用于停止轮询
 */
export function watchSpaceStatus(spaceId, onStatusChange, pollInterval = 3000) {
  return setInterval(async () => {
    try {
      const data = await getMapSpaces()
      const space = data.data.find(s => s.space_id === spaceId)
      if (space) {
        onStatusChange(space)
      }
    } catch (error) {
      console.error(`监听 ${spaceId} 失败:`, error)
    }
  }, pollInterval)
}

/**
 * 停止监听车位状态
 * 
 * @param {number} watchId - watchSpaceStatus 返回的轮询 ID
 */
export function unwatchSpaceStatus(watchId) {
  clearInterval(watchId)
}

/**
 * 模拟硬件推送（用于开发测试）
 * 
 * @param {Object} options
 * @param {string} options.spaceId - 车位 ID
 * @param {string} options.eventType - 事件类型
 * @param {string} [options.plateNumber] - 车牌号
 */
export async function simulateHardwareEvent(options) {
  const {
    spaceId,
    eventType = 'space_occupied',
    plateNumber = ''
  } = options
  
  const event = {
    event_type: eventType,
    space_id: spaceId,
    plate_number: plateNumber,
    timestamp: new Date().toISOString()
  }
  
  return pushSpaceStatusEvent(event)
}

// ========== 错误处理工具 ==========

/**
 * 解析 API 错误响应
 * 
 * @param {Error} error - Axios 错误对象
 * @returns {string} 用户友好的错误消息
 */
export function getErrorMessage(error) {
  if (error.response?.data?.error) {
    return error.response.data.error
  }
  if (error.response?.status === 404) {
    return '请求的资源不存在'
  }
  if (error.response?.status === 400) {
    return '请求参数有误'
  }
  if (error.response?.status === 500) {
    return '服务器错误，请稍后重试'
  }
  if (error.message === 'Network Error') {
    return '网络连接失败'
  }
  return error.message || '发生未知错误'
}
