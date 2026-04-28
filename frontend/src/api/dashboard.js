/**
 * 管理后台仪表盘 API
 *
 * 对应后端端点：/api/v1/dashboard/
 */

import request from './request'

/** [管理端] 获取仪表盘汇总数据 */
export function getDashboardOverview() {
  return request.get('/dashboard/overview/')
}
