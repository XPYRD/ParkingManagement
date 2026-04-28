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

/** 更新订阅（例如停用） */
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

/** 首页免登录快速缴费 */
export function quickPayQuoteNoLogin(plateNumber) {
  return request.post('/payments/records/quick-pay/quote/', {
    plate_number: plateNumber,
  })
}

/** 首页免登录快速缴费 */
export function quickPayNoLogin(plateNumber, amount, method = 'wechat', sessionId = null) {
  return request.post('/payments/records/quick-pay/', {
    plate_number: plateNumber,
    amount,
    method,
    session_id: sessionId,
  })
}

/** 首页快速缴费：模拟车辆已出场 */
export function quickPayMarkExit(plateNumber, sessionId = null) {
  return request.post('/payments/records/quick-pay/mark-exit/', {
    plate_number: plateNumber,
    session_id: sessionId,
  })
}

// ============================================================
// 充值记录
// ============================================================

/** 获取充值记录 */
export function getTopUpRecords(params) {
  return request.get('/payments/topups/', { params })
}
