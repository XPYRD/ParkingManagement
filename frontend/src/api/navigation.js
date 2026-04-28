/**
 * navigation.js — 路径规划 API 调用
 * 
 * 用于前端调用后端 Dijkstra 路径规划模块
 */

import request from './request'

/**
 * 获取两个停车位之间的最短路径
 * 
 * @param {number} startSpotId - 起点停车位 ID
 * @param {number} endSpotId - 终点停车位 ID
 * @returns {Promise} 路径信息：{path, distance, steps}
 * 
 * 示例：
 *   const path = await navigation.findPath(1, 5)
 *   // 返回：
 *   // {
 *   //   path: ['A-01', 'A-02', 'B-02', 'B-05'],
 *   //   distance: 45.5,
 *   //   steps: [
 *   //     { from: 'A-01', to: 'A-02', distance: 1.5, from_coords: [100, 200], to_coords: [150, 200] },
 *   //     ...
 *   //   ]
 *   // }
 */
export const findPath = (startSpotId, endSpotId) => {
  return request.post('/parking/navigation/find-path/', {
    start_spot_id: startSpotId,
    end_spot_id: endSpotId,
  })
}

/**
 * 获取停车位连接列表（管理端配置拓扑结构）
 * 
 * @param {Object} filters - 筛选条件
 *   - from_spot: 起点车位 ID
 *   - to_spot: 终点车位 ID
 * @returns {Promise} 连接列表
 */
export const getConnections = (filters = {}) => {
  return request.get('/parking/connections/', { params: filters })
}

/**
 * 创建停车位连接（管理端）
 * 
 * @param {number} fromSpotId - 起点车位 ID
 * @param {number} toSpotId - 终点车位 ID
 * @param {number} distance - 距离（米）
 * @returns {Promise} 创建的连接
 */
export const createConnection = (fromSpotId, toSpotId, distance = 1.0) => {
  return request.post('/parking/connections/', {
    from_spot: fromSpotId,
    to_spot: toSpotId,
    distance,
  })
}

/**
 * 删除停车位连接（管理端）
 * 
 * @param {number} connectionId - 连接 ID
 * @returns {Promise}
 */
export const deleteConnection = (connectionId) => {
  return request.delete(`/parking/connections/${connectionId}/`)
}

export default {
  findPath,
  getConnections,
  createConnection,
  deleteConnection,
}
