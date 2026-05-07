/**
 * 支付相关 API
 *
 * 对应后端端点：/api/v1/payments/
 */

import request from './request'

// ============================================================
// 支付记录
// ============================================================

/** 获取支付记录列表 */
export function getPayments(params) {
  return request.get('/payments/records/', { params })
}

/** [管理端] 获取营收汇总 */
export function getRevenueSummary() {
  return request.get('/payments/records/summary/')
}

// ============================================================
// 订阅
// ============================================================

/** 获取我的订阅列表 */
export function getSubscriptions(params) {
  return request.get('/payments/subscriptions/', { params })
}

/** 获取套餐列表（实时） */
export function getSubscriptionPlans(params) {
  return request.get('/payments/subscription-plans/', { params })
}

/** 创建订阅 */
export function createSubscription(data) {
  return request.post('/payments/subscriptions/', data)
}

/** 更新订阅 */
export function updateSubscription(id, data) {
  return request.patch(`/payments/subscriptions/${id}/`, data)
}

// ============================================================
// 定价规则
// ============================================================

/** 获取定价规则 */
export function getPricingRules() {
  return request.get('/payments/rules/')
}

/** [管理端] 更新定价规则 */
export function updatePricingRule(id, data) {
  return request.put(`/payments/rules/${id}/`, data)
}

/** [管理端] 创建定价规则 */
export function createPricingRule(data) {
  return request.post('/payments/rules/', data)
}

/** [管理端] 删除定价规则 */
export function deletePricingRule(id) {
  return request.delete(`/payments/rules/${id}/`)
}

// ============================================================
// 用户余额管理
// ============================================================

/** 获取用户余额 */
export function getUserBalance() {
  return request.get('/payments/balance/')
}

/** 充值余额 */
export function topupBalance(amount, paymentMethod) {
  return request.post('/payments/balance/topup/', {
    amount,
    payment_method: paymentMethod
  })
}

/** 确认充值（沙箱模拟扫码完成） */
export function confirmTopup(transactionId, success = true) {
  return request.post('/payments/balance/topup-confirm/', {
    transaction_id: transactionId,
    success
  })
}

/** 使用余额支付 */
export function payWithBalance(amount, sessionId, remark = '余额支付') {
  return request.post('/payments/balance/pay/', {
    amount,
    session_id: sessionId,
    remark
  })
}

/** 余额支付退款补偿 */
export function refundBalancePayment(transactionId, reason = '预约失败自动补偿') {
  return request.post('/payments/balance/refund/', {
    transaction_id: transactionId,
    reason
  })
}

/** 创建沙箱扫码支付订单（微信/支付宝/银行卡） */
export function createSandboxPayment(amount, method, sessionId, remark = '停车费支付') {
  return request.post('/payments/records/sandbox-create/', {
    amount,
    method,
    session_id: sessionId,
    remark
  })
}

/** 确认沙箱扫码支付 */
export function confirmSandboxPayment(transactionId, success = true) {
  return request.post('/payments/records/sandbox-confirm/', {
    transaction_id: transactionId,
    success
  })
}

// ============================================================
// 充值记录
// ============================================================

/** 获取充值记录 */
export function getTopUpRecords(params) {
  return request.get('/payments/topups/', { params })
}

// ============================================================
// 快速缴费（无需登录 — 首页扫码缴费流程）
// ============================================================

/** 根据车牌号查询当前停车会话（快速缴费·获取报价） */
export function quickPayQuoteNoLogin(plate) {
  return request.get('/parking/sessions/by-plate/', {
    params: { plate },
    __suppressToast: true,  // 404 = 车辆不在场，属于正常业务状态
  })
}

/** 快速缴费：创建支付订单或检查订阅免费（有 session_id 的场景） */
export function quickPayNoLogin(plate, amount, method, sessionId) {
  return request.post(`/parking/sessions/${sessionId}/quick-pay/`, {
    plate_number: plate,
    amount,
    method,
  })
}

/** 快速缴费：通过车牌号直接缴费（无 session_id 的场景） */
export function quickPayByPlate(plate, amount, method) {
  return request.post('/parking/sessions/quick-pay-by-plate/', {
    plate_number: plate,
    amount,
    method,
  })
}

/** 确认快速缴费完成（模拟支付成功），设置车位为待出场状态 */
export function confirmQuickPay(sessionId, plate) {
  return request.post('/parking/sessions/confirm-quick-pay/', {
    session_id: sessionId,
    plate_number: plate,
  })
}

/** 标记车辆出场（模拟出场，有 session_id 的场景） */
export function quickPayMarkExit(plate, sessionId) {
  return request.post(`/parking/sessions/${sessionId}/mark-exit/`, {
    plate_number: plate,
  })
}

/** 标记车辆出场（模拟出场，无 session_id 的场景，按车牌直接出场） */
export function quickPayMarkExitByPlate(plate) {
  return request.post('/parking/sessions/mark-exit-by-plate/', {
    plate_number: plate,
  })
}

// ============================================================
// 银行卡管理
// ============================================================

/** 获取我的银行卡列表 */
export function getBankCards(params) {
  return request.get('/payments/bank-cards/', { params })
}

/** 添加银行卡 */
export function addBankCard(data) {
  return request.post('/payments/bank-cards/', data)
}
