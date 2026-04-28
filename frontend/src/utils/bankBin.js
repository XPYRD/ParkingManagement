const BANK_RULES = [
  {
    name: '中国工商银行',
    icon: '/银行-工商.svg',
    prefixes: ['620058', '620200', '620302', '622200', '622202', '622203', '622208', '621226', '955880'],
  },
  {
    name: '中国农业银行',
    icon: '/银行-农行.svg',
    prefixes: ['622840', '622841', '622843', '622845', '622846', '622848', '622849', '621336', '95599'],
  },
  {
    name: '中国建设银行',
    icon: '/银行-建设.svg',
    prefixes: ['436742', '622280', '622700', '622725', '622728', '621700', '621284', '621724'],
  },
  {
    name: '中国银行',
    icon: '/银行-中国银行.svg',
    prefixes: ['621660', '621661', '621663', '621668', '621669', '621785', '621786', '621758', '625140'],
  },
  {
    name: '交通银行',
    icon: '/银行-交通.svg',
    prefixes: ['405512', '622258', '622259', '622260', '622261', '622262', '622689', '622690'],
  },
  {
    name: '招商银行',
    icon: '/银行-招商.svg',
    prefixes: ['439188', '521302', '545619', '622575', '622576', '622577', '622579', '621286', '628262'],
  },
  {
    name: '平安银行',
    icon: '/银行-平安.svg',
    prefixes: ['602907', '622155', '622156', '622157', '622316', '622986', '621626', '623058'],
  },
  {
    name: '浦发银行',
    icon: '/银行-浦发.svg',
    prefixes: ['622517', '622518', '622519', '622520', '622521', '622522', '622523', '622525', '622528', '625957'],
  },
  {
    name: '中国邮政银行',
    icon: '/银行-邮政储蓄.svg',
    prefixes: ['622150', '622151', '622181', '622188', '621098', '621799', '620529', '623218'],
  },
  {
    name: '中信银行',
    icon: '/银行-中信.svg',
    prefixes: ['403391', '403392', '433670', '433680', '622690', '622691', '622692', '622693', '622696', '621771'],
  },
  {
    name: '中国民生银行',
    icon: '/银行-民生.svg',
    prefixes: ['356827', '421865', '421869', '622620', '622621', '622622', '622623', '622624', '623622'],
  },
  {
    name: '兴业银行',
    icon: '/银行-兴业.svg',
    prefixes: ['438588', '622901', '622902', '622908', '622909', '622922', '622923', '625906', '625907'],
  },
  {
    name: '广发银行',
    icon: '/银行卡.svg',
    prefixes: ['622555', '622556', '622568', '622569', '622580', '628259', '628260'],
  },
  {
    name: '中国光大银行',
    icon: '/银行-光大.svg',
    prefixes: ['303', '356837', '622660', '622662', '622663', '622664', '622665', '622666', '622667'],
  },
  {
    name: '华夏银行',
    icon: '/银行-华夏.svg',
    prefixes: ['539867', '539868', '622630', '622631', '622632', '622633', '623020'],
  },
  {
    name: '北京银行',
    icon: '/银行卡.svg',
    prefixes: ['602969', '622163', '622853', '621030', '623111'],
  },
  {
    name: '上海银行',
    icon: '/银行-上海.svg',
    prefixes: ['622892', '622893', '622897', '621172', '623058'],
  },
  {
    name: '江苏银行',
    icon: '/银行卡.svg',
    prefixes: ['622309', '622310', '622311', '622312', '625902'],
  },
  {
    name: '宁波银行',
    icon: '/银行-宁波.svg',
    prefixes: ['622138', '622332', '622333', '625138'],
  },
  {
    name: '南京银行',
    icon: '/银行-南京.svg',
    prefixes: ['622303', '622977', '622978', '625318'],
  },
  {
    name: '杭州银行',
    icon: '/银行-杭州.svg',
    prefixes: ['622926', '622927', '622928', '625099'],
  },
  {
    name: '浙商银行',
    icon: '/银行-浙商.svg',
    prefixes: ['622252', '622253', '622233', '625096'],
  },
  {
    name: '恒丰银行',
    icon: '/银行-恒丰.svg',
    prefixes: ['622384', '622385', '622386', '625311'],
  },
  {
    name: '东亚银行',
    icon: '/银行-东亚.svg',
    prefixes: ['622500', '622506', '622507', '625301'],
  },
  {
    name: '汇丰银行',
    icon: '/银行-汇丰.svg',
    prefixes: ['622673', '622675', '625145', '625146'],
  },
  {
    name: '渣打银行',
    icon: '/银行-渣打.svg',
    prefixes: ['625138', '625139', '625140', '625141'],
  },
  {
    name: '花旗银行',
    icon: '/银行-花旗.svg',
    prefixes: ['622658', '622659', '625912', '625913'],
  },
  {
    name: '苏宁银行',
    icon: '/银行-苏宁.svg',
    prefixes: ['621483', '621729', '621492', '625961'],
  },
]

const UNKNOWN_BANK = {
  name: '暂未识别（请核对卡号）',
  icon: '/银行卡.svg',
}

const BANK_ICON_ALIASES = [
  { keywords: ['工商'], icon: '/银行-工商.svg' },
  { keywords: ['农业', '农行'], icon: '/银行-农行.svg' },
  { keywords: ['建设', '建行'], icon: '/银行-建设.svg' },
  { keywords: ['中国银行', '中行'], icon: '/银行-中国银行.svg' },
  { keywords: ['交通', '交行'], icon: '/银行-交通.svg' },
  { keywords: ['招商', '招行'], icon: '/银行-招商.svg' },
  { keywords: ['平安'], icon: '/银行-平安.svg' },
  { keywords: ['浦发'], icon: '/银行-浦发.svg' },
  { keywords: ['邮政储蓄', '邮储'], icon: '/银行-邮政储蓄.svg' },
  { keywords: ['中信'], icon: '/银行-中信.svg' },
  { keywords: ['民生'], icon: '/银行-民生.svg' },
  { keywords: ['兴业'], icon: '/银行-兴业.svg' },
  { keywords: ['光大'], icon: '/银行-光大.svg' },
  { keywords: ['华夏'], icon: '/银行-华夏.svg' },
  { keywords: ['上海'], icon: '/银行-上海.svg' },
  { keywords: ['宁波'], icon: '/银行-宁波.svg' },
  { keywords: ['南京'], icon: '/银行-南京.svg' },
  { keywords: ['杭州'], icon: '/银行-杭州.svg' },
  { keywords: ['浙商'], icon: '/银行-浙商.svg' },
  { keywords: ['恒丰'], icon: '/银行-恒丰.svg' },
  { keywords: ['东亚'], icon: '/银行-东亚.svg' },
  { keywords: ['汇丰'], icon: '/银行-汇丰.svg' },
  { keywords: ['渣打'], icon: '/银行-渣打.svg' },
  { keywords: ['花旗'], icon: '/银行-花旗.svg' },
  { keywords: ['苏宁'], icon: '/银行-苏宁.svg' },
]

export function normalizeCardNumber(raw) {
  return String(raw || '').replace(/\D/g, '')
}

export function formatCardNumber(rawCardNumber) {
  const number = normalizeCardNumber(rawCardNumber).slice(0, 19)
  return number.replace(/(\d{4})(?=\d)/g, '$1 ').trim()
}

export function detectBankByCardNumber(rawCardNumber) {
  const number = normalizeCardNumber(rawCardNumber)
  if (number.length < 6) {
    return null
  }

  let matchedBank = null
  let longestPrefixLength = 0

  for (const bank of BANK_RULES) {
    for (const prefix of bank.prefixes) {
      if (number.startsWith(prefix) && prefix.length > longestPrefixLength) {
        matchedBank = bank
        longestPrefixLength = prefix.length
      }
    }
  }

  return matchedBank || UNKNOWN_BANK
}

export function resolveBankIconByName(bankName) {
  const name = String(bankName || '').trim()
  if (!name) {
    return UNKNOWN_BANK.icon
  }

  const exact = BANK_RULES.find((item) => item.name === name)
  if (exact) {
    return exact.icon
  }

  const fuzzy = BANK_ICON_ALIASES.find((item) => item.keywords.some((keyword) => name.includes(keyword)))
  if (fuzzy) {
    return fuzzy.icon
  }

  return UNKNOWN_BANK.icon
}

export function isValidLuhn(rawCardNumber) {
  const number = normalizeCardNumber(rawCardNumber)
  if (!/^\d{16,19}$/.test(number)) {
    return false
  }

  let sum = 0
  let shouldDouble = false

  for (let i = number.length - 1; i >= 0; i -= 1) {
    let digit = Number(number[i])
    if (shouldDouble) {
      digit *= 2
      if (digit > 9) {
        digit -= 9
      }
    }
    sum += digit
    shouldDouble = !shouldDouble
  }

  return sum % 10 === 0
}

export function detectCardTypeByCardNumber(rawCardNumber) {
  const number = normalizeCardNumber(rawCardNumber)
  if (number.length < 2) {
    return null
  }

  if (/^62/.test(number)) {
    if (/^625|^6282/.test(number)) {
      return '信用卡'
    }
    return '借记卡'
  }

  if (/^4|^5|^35|^36|^37|^30/.test(number)) {
    return '信用卡'
  }

  if (/^9/.test(number)) {
    return '借记卡'
  }

  return '未知卡类型'
}

export { BANK_RULES }