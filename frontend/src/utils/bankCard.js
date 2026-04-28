const BANK_CARD_BOUND_KEY = 'sentinel_has_bound_bank_card'

export function hasBoundBankCard() {
  try {
    return window.localStorage.getItem(BANK_CARD_BOUND_KEY) === '1'
  } catch (err) {
    return false
  }
}

export function setBankCardBound(bound) {
  try {
    window.localStorage.setItem(BANK_CARD_BOUND_KEY, bound ? '1' : '0')
  } catch (err) {
    // ignore storage exceptions
  }
}
