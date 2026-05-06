<template>
  <div class="px-4 md:px-8 max-w-7xl mx-auto py-8">
    <header class="mb-8 text-center max-w-2xl mx-auto">
      <h1 class="text-3xl font-extrabold text-primary tracking-tight font-headline">预约车位</h1>
      <p class="text-secondary text-sm mt-2">提前锁定专属位置，享受无缝停车体验。支持最多提前 7 天预约。</p>
    </header>

    <div class="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
      <div class="bg-surface-container-lowest p-6 md:p-8 rounded-3xl shadow-lg border border-outline-variant/10 relative overflow-hidden">
        <div class="absolute top-0 w-full h-1 left-0 bg-gradient-to-r from-primary to-blue-300"></div>
        <h2 class="text-xl font-bold font-headline text-on-surface mb-6">配置预约信息</h2>

        <el-form label-position="top" class="space-y-5">
          <el-form-item label="入场日期">
            <el-date-picker
              v-model="reserveForm.date"
              type="date"
              placeholder="请选择入场日期"
              size="large"
              class="!w-full"
              :disabled-date="disableStartDate"
            />
          </el-form-item>

          <el-form-item label="离开日期">
            <el-date-picker
              v-model="reserveForm.endDate"
              type="date"
              placeholder="请选择离开日期"
              size="large"
              class="!w-full"
              :disabled-date="disableEndDate"
            />
          </el-form-item>

          <div class="grid grid-cols-2 gap-4">
            <el-form-item label="入场时间">
              <el-time-select v-model="reserveForm.startTime" start="06:00" step="00:15" end="23:45" placeholder="选择" size="large" class="!w-full" />
            </el-form-item>
            <el-form-item label="预计离场">
              <el-time-select v-model="reserveForm.endTime" start="06:00" step="00:15" end="23:45" placeholder="选择" size="large" class="!w-full" />
            </el-form-item>
          </div>

          <el-form-item label="车位类型偏好">
            <el-radio-group v-model="reserveForm.type" class="!flex !w-full gap-2">
              <el-radio-button label="standard" class="flex-1 text-center">标准</el-radio-button>
              <el-radio-button label="ev" class="flex-1 text-center">充电桩</el-radio-button>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="关联车辆">
            <el-select v-model="reserveForm.vehicle" placeholder="请选择车辆" size="large" class="w-full">
              <el-option
                v-for="car in myCars"
                :key="car.id"
                :label="`${car.plate_number} (${getVehicleTypeLabel(car.vehicle_type)})`"
                :value="car.id"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </div>

      <div class="space-y-6">
        <div class="bg-primary text-white p-6 md:p-8 rounded-3xl shadow-xl relative overflow-hidden">
          <div class="absolute -bottom-10 -right-10 opacity-10">
            <span class="material-symbols-outlined" style="font-size: 160px;">confirmation_number</span>
          </div>

          <h3 class="text-sm font-bold uppercase tracking-widest text-white/80 mb-6">预估明细</h3>

          <div class="space-y-4 mb-8">
            <div class="flex justify-between items-center text-sm">
              <span class="text-white/70">预约基础费</span>
              <span class="font-bold">¥ {{ dailyReservationFee.toFixed(2) }}/天</span>
            </div>
            <div class="flex justify-between items-center text-sm">
              <span class="text-white/70">计费天数</span>
              <span class="font-bold">{{ billingDays }} 天</span>
            </div>
            <div class="flex justify-between items-center text-sm" v-if="reserveForm.type === 'ev'">
              <span class="text-white/70">充电桩附加费</span>
              <span class="font-bold">¥ {{ evSurcharge.toFixed(2) }}</span>
            </div>

            <div class="border-t border-white/20 pt-4 mt-2 flex justify-between items-center">
              <span class="font-bold uppercase tracking-widest">预付总额</span>
              <span class="text-3xl font-black font-headline text-amber-300">¥ {{ totalFee.toFixed(2) }}</span>
            </div>
          </div>

          <el-button type="warning" size="large" class="!w-full !rounded-xl !font-bold !py-6 shadow-xl shadow-amber-500/20 border-0" :loading="loading" @click="handleConfirm">
            确认并支付
          </el-button>
          <p class="text-[10px] text-white/50 text-center mt-4">
            *预约开始前2小时可全额退款。超时未入场不予退还。
          </p>
        </div>

        <div class="bg-surface-container-lowest p-6 rounded-2xl border border-outline-variant/20 shadow-sm text-sm">
          <h4 class="font-bold text-on-surface mb-3 flex items-center gap-2">
            <span class="material-symbols-outlined text-sm text-primary">info</span>
            预约规则说明
          </h4>
          <ul class="space-y-2 text-secondary text-xs list-disc list-inside">
            <li>系统将为您保留车位直至预定离场时间结束。</li>
            <li>入场时请确保使用所绑定的车牌进行无感进入，以激活预约订单。</li>
          </ul>
        </div>
      </div>
    </div>

    <el-dialog
      v-model="showPaymentDialog"
      title="选择支付方式"
      width="90%"
      max-width="460px"
      :close-on-click-modal="false"
    >
      <div class="mb-3 text-xs text-secondary">
        账户余额：
        <span class="font-semibold text-on-surface" v-if="!loadingBalance">¥ {{ userBalance.toFixed(2) }}</span>
        <span class="font-semibold text-on-surface" v-else>加载中...</span>
      </div>
      <div class="space-y-3">
        <label
          v-for="method in paymentMethods"
          :key="method.value"
          class="flex items-center justify-between p-3 rounded-lg border border-outline-variant/40 transition"
          :class="method.disabled ? 'opacity-50 cursor-not-allowed bg-slate-50' : 'cursor-pointer hover:bg-slate-50'"
          @click="selectPaymentMethod(method)"
        >
          <div class="flex items-center gap-3">
            <input type="radio" :value="method.value" v-model="selectedPaymentMethod" class="w-4 h-4" :disabled="method.disabled" />
            <img :src="method.icon" :alt="method.label" class="w-6 h-6 object-contain" />
            <span class="font-semibold text-on-surface">{{ method.label }}</span>
          </div>
          <span class="text-xs text-secondary">{{ method.desc }}</span>
        </label>
      </div>
      <template #footer>
        <div class="flex gap-3">
          <el-button @click="showPaymentDialog = false">取消</el-button>
          <el-button type="primary" :loading="loading" @click="handlePaymentConfirm">确认支付</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, computed, ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { getVehicles } from '@/api/user'
import { getSpots, createReservation } from '@/api/parking'
import { getPricingRules, getUserBalance, payWithBalance, refundBalancePayment } from '@/api/payment'

const router = useRouter()

const dailyReservationFee = ref(30.0)
const evSurcharge = ref(10.0)

const reserveForm = reactive({
  date: null,
  endDate: null,
  startTime: '08:00',
  endTime: '12:00',
  type: 'standard',
  vehicle: ''
})

const myCars = ref([])
const loading = ref(false)
const showPaymentDialog = ref(false)
const selectedPaymentMethod = ref('balance')
const userBalance = ref(0)
const loadingBalance = ref(false)

const vehicleTypeLabelMap = {
  car: '小型车',
  suv: 'SUV',
  truck: '货车'
}

const billingDays = computed(() => {
  if (!reserveForm.date) return 1
  const startDate = new Date(reserveForm.date)
  const endDate = new Date(reserveForm.endDate || reserveForm.date)
  if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) return 1
  const diffDays = Math.floor((endDate.getTime() - startDate.getTime()) / (24 * 60 * 60 * 1000)) + 1
  return Math.max(1, diffDays)
})

const totalFee = computed(() => {
  let amount = dailyReservationFee.value * billingDays.value
  if (reserveForm.type === 'ev') amount += evSurcharge.value
  return amount
})

const isBalanceEnough = computed(() => userBalance.value >= totalFee.value)

const paymentMethods = computed(() => [
  {
    value: 'balance',
    label: '余额支付',
    desc: isBalanceEnough.value ? `余额 ¥${userBalance.value.toFixed(2)}` : `余额不足(当前 ¥${userBalance.value.toFixed(2)})`,
    icon: '/余额.svg',
    disabled: !isBalanceEnough.value
  },
  { value: 'wechat', label: '微信支付', desc: '推荐', icon: '/微信支付.svg', disabled: false },
  { value: 'alipay', label: '支付宝', desc: '快捷', icon: '/支付宝支付.svg', disabled: false },
  { value: 'card', label: '银行卡', desc: '安全', icon: '/银行卡.svg', disabled: false }
])

watch(
  () => reserveForm.date,
  (value) => {
    if (!value) return
    if (!reserveForm.endDate) {
      reserveForm.endDate = value
      return
    }
    if (new Date(reserveForm.endDate) < new Date(value)) {
      reserveForm.endDate = value
    }
  }
)

function disableStartDate(time) {
  return time.getTime() < Date.now() - 8.64e7
}

function disableEndDate(time) {
  if (!reserveForm.date) {
    return time.getTime() < Date.now() - 8.64e7
  }
  const start = new Date(reserveForm.date)
  start.setHours(0, 0, 0, 0)
  return time.getTime() < start.getTime()
}

function getVehicleTypeLabel(vehicleType) {
  return vehicleTypeLabelMap[String(vehicleType || '').toLowerCase()] || '普通车'
}

function toDateString(d) {
  return [
    d.getFullYear(),
    String(d.getMonth() + 1).padStart(2, '0'),
    String(d.getDate()).padStart(2, '0')
  ].join('-')
}

async function loadPricingRules() {
  try {
    const res = await getPricingRules()
    const rows = res.results || res || []
    const ruleMap = Object.fromEntries(rows.map((item) => [item.rate_type, item]))
    dailyReservationFee.value = Number(ruleMap.reservation_daily?.value || 30.0)
    evSurcharge.value = Number(ruleMap.reservation_ev_surcharge?.value || 10.0)
  } catch (err) {
    console.error('加载预约定价规则失败', err)
  }
}

async function loadUserBalance() {
  loadingBalance.value = true
  try {
    const res = await getUserBalance()
    userBalance.value = Number(res?.data?.balance || res?.balance || 0)
  } catch (err) {
    userBalance.value = 0
    console.error('加载账户余额失败', err)
  } finally {
    loadingBalance.value = false
  }
}

onMounted(async () => {
  await loadPricingRules()
  await loadUserBalance()
  try {
    const res = await getVehicles()
    myCars.value = res.results || res
    if (myCars.value.length > 0) {
      reserveForm.vehicle = myCars.value[0].id
    }
  } catch (err) {
    ElMessage.error('无法加载车辆信息')
  }
})

async function handleConfirm() {
  if (!reserveForm.date || !reserveForm.endDate || !reserveForm.startTime || !reserveForm.endTime) {
    ElMessage.warning('请完整配置日期和时间信息')
    return
  }
  if (!reserveForm.vehicle) {
    ElMessage.warning('请选择关联的车辆')
    return
  }

  await loadUserBalance()
  if (!isBalanceEnough.value && selectedPaymentMethod.value === 'balance') {
    selectedPaymentMethod.value = 'wechat'
  }

  showPaymentDialog.value = true
}

function selectPaymentMethod(method) {
  if (method.disabled) {
    ElMessage.warning('余额不足，请先充值后再使用余额支付')
    return
  }
  selectedPaymentMethod.value = method.value
}

async function submitReservation() {
  loading.value = true
  let balancePaid = false
  let balanceTxnId = ''
  try {
    const spotRes = await getSpots({ status: 'free', spot_type: reserveForm.type })
    const spots = spotRes.results || spotRes
    if (spots.length === 0) {
      ElMessage.error('抱歉，当前类别车位已被预约满，请更换类型！')
      return
    }

    if (selectedPaymentMethod.value === 'balance') {
      const payRes = await payWithBalance(totalFee.value, null, '预约车位费用')
      balancePaid = true
      balanceTxnId = String(payRes?.transaction_id || payRes?.data?.transaction_id || '')
    }

    await createReservation({
      spot: spots[0].id,
      date: toDateString(new Date(reserveForm.date)),
      end_date: toDateString(new Date(reserveForm.endDate)),
      start_time: reserveForm.startTime,
      end_time: reserveForm.endTime,
      total_amount: totalFee.value,
      payment_method: selectedPaymentMethod.value
    })

    ElMessage.success('预约成功，请准时入场！')
    showPaymentDialog.value = false
    await loadUserBalance()
    router.push('/profile')
  } catch (err) {
    const detail = String(err?.response?.data?.detail || '')
    if (selectedPaymentMethod.value === 'balance' && detail.includes('余额不足')) {
      ElMessage.error('余额不足，请先充值后再支付')
    } else if (selectedPaymentMethod.value === 'balance' && balancePaid) {
      try {
        if (balanceTxnId) {
          await refundBalancePayment(balanceTxnId, '预约创建失败自动补偿')
          await loadUserBalance()
          ElMessage.error('预约失败，已自动退回余额。')
        } else {
          ElMessage.error('预约失败，余额可能已扣款，请联系客服处理。')
        }
      } catch (refundErr) {
        console.error('自动退款失败', refundErr)
        ElMessage.error('预约失败，自动退款失败，请联系客服处理。')
      }
    } else {
      ElMessage.error('系统繁忙，预约失败，请稍后重试。')
    }
    console.error(err)
  } finally {
    loading.value = false
  }
}

function handlePaymentConfirm() {
  if (!selectedPaymentMethod.value) {
    ElMessage.warning('请选择支付方式')
    return
  }

  if (selectedPaymentMethod.value === 'balance' && !isBalanceEnough.value) {
    ElMessageBox.confirm(
      `当前余额 ¥${userBalance.value.toFixed(2)}，不足以支付 ¥${totalFee.value.toFixed(2)}，是否前往充值？`,
      '余额不足',
      { confirmButtonText: '去充值', cancelButtonText: '取消', type: 'warning' }
    ).then(() => {
      showPaymentDialog.value = false
      router.push('/payment')
    }).catch(() => {})
    return
  }

  const methodLabel = paymentMethods.value.find((m) => m.value === selectedPaymentMethod.value)?.label || '当前方式'

  ElMessageBox.confirm(
    `即将使用${methodLabel}支付 ¥${totalFee.value.toFixed(2)} 用于锁定车位，是否确认？`,
    '确认支付',
    { confirmButtonText: '确认支付', cancelButtonText: '取消', type: 'warning' }
  ).then(() => submitReservation()).catch(() => {})
}
</script>
