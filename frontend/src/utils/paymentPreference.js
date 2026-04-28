const DEFAULT_PAYMENT_METHOD_KEY = 'sentinel_default_payment_method'

const ALLOWED_METHODS = new Set(['balance', 'wechat', 'alipay', 'card'])

export function getDefaultPaymentMethod(fallback = 'wechat') {
  try {
    const value = window.localStorage.getItem(DEFAULT_PAYMENT_METHOD_KEY)
    if (value && ALLOWED_METHODS.has(value)) {
      return value
    }
  } catch (err) {
    // ignore storage exceptions
  }
  return fallback
}

export function setDefaultPaymentMethod(method) {
  if (!ALLOWED_METHODS.has(method)) return
  try {
    window.localStorage.setItem(DEFAULT_PAYMENT_METHOD_KEY, method)
  } catch (err) {
    // ignore storage exceptions
  }
}
