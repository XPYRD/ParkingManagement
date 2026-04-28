<template>
  <el-dialog
    v-model="dialogVisible"
    :title="title"
    width="90%"
    max-width="460px"
    :close-on-click-modal="false"
    destroy-on-close
    @closed="resetDialogState"
  >
    <div class="space-y-4">
      <div>
        <label class="block text-sm font-semibold text-slate-700 mb-2">持卡人姓名</label>
        <el-input v-model="bankCardForm.holder" placeholder="请输入持卡人姓名" />
      </div>

      <div>
        <label class="block text-sm font-semibold text-slate-700 mb-2">银行卡号</label>
        <el-input
          v-model="bankCardForm.number"
          placeholder="请输入16-19位银行卡号"
          :maxlength="23"
          :formatter="formatCardNumber"
          :parser="parseCardNumber"
        />
        <div v-if="detectedBank" class="mt-2 flex items-center gap-2 text-sm">
          <img
            :src="detectedBank.icon"
            :alt="detectedBank.name"
            class="h-11 w-11 rounded-md border border-slate-200 bg-white p-1 object-contain shadow-sm"
          />
          <span class="font-semibold text-slate-800">{{ detectedBank.name }}</span>
        </div>
        <p v-if="detectedCardType" class="mt-1 text-xs text-slate-500">
          卡类型：{{ detectedCardType }}
        </p>
        <p v-if="showLuhnHint" class="mt-1 text-xs" :class="isCardNumberValid ? 'text-emerald-600' : 'text-rose-500'">
          {{ isCardNumberValid ? '卡号校验通过' : '卡号校验未通过，请确认输入是否正确' }}
        </p>
      </div>

      <div>
        <label class="block text-sm font-semibold text-slate-700 mb-2">预留手机号</label>
        <el-input
          v-model="bankCardForm.phone"
          placeholder="请输入11位手机号"
          maxlength="11"
          @input="bankCardForm.phone = String(bankCardForm.phone || '').replace(/\D/g, '')"
        />
      </div>

      <div>
        <label class="block text-sm font-semibold text-slate-700 mb-2">验证码</label>
        <div class="flex gap-2">
          <el-input v-model="bankCardForm.code" placeholder="请输入6位验证码" maxlength="6" />
          <el-button :disabled="!canRequestCode" @click="requestBankCardCode">
            {{ requestCodeText }}
          </el-button>
        </div>
        <p v-if="!canRequestCode && requestCodeBlockReason" class="mt-1 text-xs text-amber-600">
          {{ requestCodeBlockReason }}
        </p>
      </div>
    </div>

    <template #footer>
      <div class="flex gap-3">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!canSubmit" @click="handleSubmit">
          {{ confirmText }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { setBankCardInfo } from '@/utils/bankCard'
import { addBankCard } from '@/api/payment'
import { detectBankByCardNumber, detectCardTypeByCardNumber, formatCardNumber, isValidLuhn, normalizeCardNumber } from '@/utils/bankBin'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: '添加银行卡',
  },
  confirmText: {
    type: String,
    default: '确认添加并验证',
  },
  requestCodeText: {
    type: String,
    default: '发送验证码',
  },
})

const emit = defineEmits(['update:modelValue', 'success'])

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const bankCardForm = reactive({
  phone: '',
  holder: '',
  number: '',
  code: '',
})

const detectedBank = computed(() => {
  return detectBankByCardNumber(bankCardForm.number)
})

const detectedCardType = computed(() => detectCardTypeByCardNumber(bankCardForm.number))
const isCardNumberValid = computed(() => isValidLuhn(bankCardForm.number))
const showLuhnHint = computed(() => /^\d{16,19}$/.test(normalizeCardNumber(bankCardForm.number)))
const isKnownBank = computed(() => Boolean(detectedBank.value && detectedBank.value.name !== '暂未识别（请核对卡号）'))
const isKnownCardType = computed(() => Boolean(detectedCardType.value && detectedCardType.value !== '未知卡类型'))

const requestCodeBlockReason = computed(() => {
  const phone = String(bankCardForm.phone || '').replace(/\D/g, '')
  const holder = String(bankCardForm.holder || '').trim()
  const number = normalizeCardNumber(bankCardForm.number)

  if (!holder) {
    return '请先输入持卡人姓名'
  }
  if (!/^1\d{10}$/.test(phone)) {
    return '请先输入正确的11位手机号'
  }
  if (!/^\d{16,19}$/.test(number)) {
    return '请输入16到19位银行卡号'
  }
  if (!isKnownBank.value) {
    return '暂未识别银行，请检查卡号'
  }
  if (!isKnownCardType.value) {
    return '暂未识别卡类型，请检查卡号'
  }
  if (!isCardNumberValid.value) {
    return '卡号校验未通过，请确认输入'
  }
  return ''
})

const canRequestCode = computed(() => !requestCodeBlockReason.value)
const canSubmit = computed(() => canRequestCode.value && !!mockCardVerifyCode.value)

function parseCardNumber(value) {
  return normalizeCardNumber(value).slice(0, 19)
}

const mockCardVerifyCode = ref('')

watch(
  () => props.modelValue,
  (visible) => {
    if (visible) {
      resetDialogState()
    }
  }
)

function resetDialogState() {
  bankCardForm.phone = ''
  bankCardForm.holder = ''
  bankCardForm.number = ''
  bankCardForm.code = ''
  mockCardVerifyCode.value = ''
}

function requestBankCardCode() {
  const phone = String(bankCardForm.phone || '').replace(/\D/g, '')
  const holder = String(bankCardForm.holder || '').trim()
  const number = String(bankCardForm.number || '').replace(/\D/g, '')

  if (!/^1\d{10}$/.test(phone)) {
    ElMessage.warning('请输入正确的11位手机号')
    return
  }
  if (!holder) {
    ElMessage.warning('请输入持卡人姓名')
    return
  }
  if (!/^\d{16,19}$/.test(number)) {
    ElMessage.warning('银行卡号需为16到19位数字')
    return
  }
  if (!isValidLuhn(number)) {
    ElMessage.warning('银行卡号校验未通过，请确认后重试')
    return
  }

  mockCardVerifyCode.value = String(Math.floor(100000 + Math.random() * 900000))
  ElMessage.success(`验证码已发送（模拟）：${mockCardVerifyCode.value}`)
}

async function handleSubmit() {
  const phone = String(bankCardForm.phone || '').replace(/\D/g, '')
  const holder = String(bankCardForm.holder || '').trim()
  const number = String(bankCardForm.number || '').replace(/\D/g, '')
  const code = String(bankCardForm.code || '').trim()

  if (!/^1\d{10}$/.test(phone)) {
    ElMessage.warning('请输入正确的11位手机号')
    return
  }
  if (!holder) {
    ElMessage.warning('请输入持卡人姓名')
    return
  }
  if (!/^\d{16,19}$/.test(number)) {
    ElMessage.warning('银行卡号需为16到19位数字')
    return
  }
  if (!isValidLuhn(number)) {
    ElMessage.warning('银行卡号校验未通过，请确认后重试')
    return
  }
  if (!mockCardVerifyCode.value) {
    ElMessage.warning('请先发送验证码')
    return
  }
  if (code !== mockCardVerifyCode.value) {
    ElMessage.error('验证码错误，请重新输入')
    return
  }

  const payload = {
    bank_name: detectedBank.value?.name || '银行卡',
    card_type: detectedCardType.value || '',
    holder_name: holder,
    card_last4: number.slice(-4),
    bin_prefix: number.slice(0, 6),
    is_default: true,
  }

  let persistedCard = null
  try {
    persistedCard = await addBankCard(payload)
  } catch (err) {
    ElMessage.error('银行卡保存失败，请稍后重试')
    return
  }

  setBankCardInfo(persistedCard || payload)
  emit('success', {
    phone,
    holder,
    number,
  })
  ElMessage.success('银行卡添加并验证成功')
  dialogVisible.value = false
}
</script>