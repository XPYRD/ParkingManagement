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

          <el-form-item label="预约楼层">
            <el-select v-model="reserveForm.floor" placeholder="请选择楼层" size="large" class="w-full">
              <el-option
                v-for="floor in floorOptions"
                :key="floor.value"
                :label="floor.label"
                :value="floor.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="预约方式">
            <el-radio-group v-model="reservationMode" class="!flex !w-full gap-2">
              <el-radio-button label="random" class="flex-1 text-center">随机分配车位</el-radio-button>
              <el-radio-button label="specific" class="flex-1 text-center">指定特定车位</el-radio-button>
            </el-radio-group>
          </el-form-item>

          <el-form-item v-if="reservationMode === 'specific'" label="指定车位">
            <el-select
              v-model="reserveForm.spotId"
              placeholder="请选择具体车位"
              size="large"
              class="w-full"
              filterable
            >
              <el-option
                v-for="spot in specificSpotOptions"
                :key="spot.id"
                :label="spot.label"
                :value="spot.id"
              />
            </el-select>
            <p v-if="reserveForm.spotSpaceId" class="mt-2 text-xs text-secondary">
              当前指定：{{ reserveForm.spotSpaceId.replace(/^space_/, '') }}
            </p>
            <p v-if="!specificSpotOptions.length" class="mt-2 text-xs text-error">
              当前楼层与类型下无可指定车位，请切换楼层或类型。
            </p>
          </el-form-item>

          <div class="rounded-xl border border-outline-variant/30 bg-slate-50 p-3">
            <div class="flex items-center justify-between text-xs text-secondary">
              <span>当前楼层可分配余量</span>
              <span v-if="loadingFloorAvailability">更新中...</span>
              <span v-else>{{ reserveForm.floor }}</span>
            </div>
            <div class="mt-2 flex items-center justify-between">
              <p class="text-sm text-on-surface">
                {{ reserveForm.type === 'ev' ? '充电桩车位' : '标准车位' }}可分配
              </p>
              <p class="text-lg font-black" :class="selectedTypeAvailableCount > 0 ? 'text-primary' : 'text-error'">
                {{ selectedTypeAvailableCount }}
              </p>
            </div>
            <p v-if="selectedTypeAvailableCount === 0" class="mt-1 text-xs text-error">
              当前楼层该类型暂无可分配车位，请切换楼层或类型。
            </p>
          </div>

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
        <div v-if="!hasBankCard" class="flex items-center justify-between rounded-lg border border-dashed border-slate-300 bg-slate-50 p-3">
          <p class="text-xs text-slate-600">未添加银行卡，当前不可使用银行卡支付</p>
          <el-button type="primary" link @click="openAddBankCardDialog">添加银行卡（模拟验证）</el-button>
        </div>
      </div>
      <template #footer>
        <div class="flex gap-3">
          <el-button @click="showPaymentDialog = false">取消</el-button>
          <el-button type="primary" :loading="loading" @click="handlePaymentConfirm">确认支付</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showAddCardDialog"
      title="添加银行卡（模拟）"
      width="90%"
      max-width="460px"
      :close-on-click-modal="false"
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
            maxlength="19"
            @input="bankCardForm.number = String(bankCardForm.number || '').replace(/\D/g, '')"
          />
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
          <label class="block text-sm font-semibold text-slate-700 mb-2">人机验证</label>
          <div class="rounded-lg border border-slate-300 p-3 bg-slate-50">
            <div class="relative h-12 rounded-md bg-gradient-to-r from-slate-100 to-slate-200 overflow-hidden mb-3">
              <div
                class="absolute top-2 w-8 h-8 rounded-md border-2 border-dashed border-slate-400 bg-white/70"
                :style="{ left: `${bankCardPuzzleTarget}px` }"
              />
              <div
                class="absolute top-2 w-8 h-8 rounded-md bg-blue-500/90 border border-white shadow transition-all duration-75"
                :style="{ left: `${bankCardPuzzleValue}px` }"
              />
            </div>
            <div class="flex gap-2 items-center">
              <input
                v-model.number="bankCardPuzzleValue"
                type="range"
                min="0"
                :max="bankCardPuzzleMax"
                class="w-full"
                :disabled="bankCardHumanVerified"
                @input="handleBankCardPuzzleSlide"
              />
              <el-button @click="resetBankCardPuzzleCaptcha">重置</el-button>
            </div>
          </div>
          <p class="text-xs mt-1" :class="bankCardHumanVerified ? 'text-emerald-600' : 'text-slate-500'">
            {{ bankCardHumanVerified ? '拼图校验通过' : '拖动滑块，让蓝色拼图块对齐虚线缺口。' }}
          </p>
        </div>

        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-2">验证码</label>
          <div class="flex gap-2">
            <el-input v-model="bankCardForm.code" placeholder="请输入验证码" maxlength="6" />
            <el-button :disabled="!bankCardHumanVerified" @click="requestBankCardCode">获取验证码</el-button>
          </div>
          <p class="text-xs text-slate-500 mt-1">需先通过拖动拼图验证，验证码为模拟发送，请在提示消息中查看。</p>
        </div>
      </div>

      <template #footer>
        <div class="flex gap-3">
          <el-button @click="showAddCardDialog = false">取消</el-button>
          <el-button type="primary" @click="confirmAddBankCard">确认添加并验证</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, computed, ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import { getVehicles } from '@/api/user'
import { getFloorSummary, createReservation, getSpacesByFloor } from '@/api/parking'
import { getPricingRules, getUserBalance, payWithBalance, refundBalancePayment } from '@/api/payment'
import { hasBoundBankCard, setBankCardBound } from '@/utils/bankCard'
import { getDefaultPaymentMethod } from '@/utils/paymentPreference'

const router = useRouter()
const route = useRoute()

const dailyReservationFee = ref(30.0)
const evSurcharge = ref(10.0)

const reserveForm = reactive({
  date: null,
  endDate: null,
  startTime: '08:00',
  endTime: '12:00',
  type: 'standard',
  floor: 'B2',
  vehicle: '',
  spotId: null,
  spotSpaceId: ''
})

const reservationMode = ref('random')

const floorOptions = ref([
  { value: 'B2', label: 'B2 地下二层' },
  { value: 'B1', label: 'B1 地下一层' },
  { value: '1F', label: '1F 一楼' }
])

const myCars = ref([])
const loading = ref(false)
const loadingFloorAvailability = ref(false)
const showPaymentDialog = ref(false)
const selectedPaymentMethod = ref('balance')
const userBalance = ref(0)
const loadingBalance = ref(false)
const floorSpots = ref([])
const hasBankCard = ref(false)
const showAddCardDialog = ref(false)
const bankCardForm = ref({
  phone: '',
  holder: '',
  number: '',
  code: '',
})
const bankCardHumanVerified = ref(false)
const bankCardPuzzleMax = 220
const bankCardPuzzleTarget = ref(0)
const bankCardPuzzleValue = ref(0)
const mockCardVerifyCode = ref('')
const floorAvailability = ref({
  total: 0,
  standard: 0,
  ev: 0,
})

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

const selectedTypeAvailableCount = computed(() => {
  return reserveForm.type === 'ev'
    ? Number(floorAvailability.value.ev || 0)
    : Number(floorAvailability.value.standard || 0)
})

const specificSpotOptions = computed(() => {
  return floorSpots.value
    .filter((spot) => {
      if (!isSpotAvailable(spot)) return false
      const isEv = Boolean(spot?.type)
      return reserveForm.type === 'ev' ? isEv : !isEv
    })
    .map((spot) => {
      const displaySpaceId = String(spot?.space_id || '').replace(/^space_/, '')
      return {
        id: Number(spot?.id),
        spaceId: String(spot?.space_id || ''),
        label: `${displaySpaceId} (${reserveForm.floor})`
      }
    })
    .filter((item) => Number.isFinite(item.id) && item.id > 0)
})

const selectedSpecificSpot = computed(() => {
  const selectedId = Number(reserveForm.spotId)
  if (!Number.isFinite(selectedId) || selectedId <= 0) return null
  return specificSpotOptions.value.find((item) => item.id === selectedId) || null
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
  { value: 'card', label: '银行卡', desc: hasBankCard.value ? '安全' : '请先添加银行卡', icon: '/银行卡.svg', disabled: !hasBankCard.value }
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

function isSpotAvailable(spot) {
  const isDamaged = Boolean(spot?.is_damaged)
  const isReserved = Boolean(String(spot?.reserved_plate || '').trim())
  const hasCurrentPlate = Boolean(String(spot?.current_plate || '').trim())
  return !isDamaged && !isReserved && !hasCurrentPlate
}

function applyRoutePrefill() {
  const queryMode = String(route.query?.reservationMode || '').toLowerCase()
  if (queryMode === 'specific') {
    reservationMode.value = 'specific'
  }

  const queryFloor = String(route.query?.floor || '').toUpperCase()
  if (queryFloor) {
    reserveForm.floor = queryFloor
  }

  const queryType = String(route.query?.spotType || '').toLowerCase()
  if (queryType === 'standard' || queryType === 'ev') {
    reserveForm.type = queryType
  }

  const querySpotId = Number(route.query?.spotId)
  if (Number.isFinite(querySpotId) && querySpotId > 0) {
    reserveForm.spotId = querySpotId
    reservationMode.value = 'specific'
  }

  const querySpaceId = String(route.query?.spaceId || '').trim()
  if (querySpaceId) {
    reserveForm.spotSpaceId = querySpaceId
  }
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

async function loadFloorOptions() {
  try {
    const res = await getFloorSummary()
    const rows = Array.isArray(res) ? res : (res?.results || [])
    if (!rows.length) return

    floorOptions.value = rows.map((item) => {
      const value = String(item.floor || '').toUpperCase()
      const labelMap = { B2: 'B2 地下二层', B1: 'B1 地下一层', '1F': '1F 一楼' }
      return {
        value,
        label: labelMap[value] || value
      }
    })

    const currentFloor = String(reserveForm.floor || '').toUpperCase()
    if (!floorOptions.value.some((item) => item.value === currentFloor)) {
      reserveForm.floor = floorOptions.value[0]?.value || 'B2'
    }
  } catch (err) {
    console.error('加载楼层选项失败', err)
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

async function loadFloorAvailability() {
  const floor = String(reserveForm.floor || '').toUpperCase()
  if (!floor) {
    floorAvailability.value = { total: 0, standard: 0, ev: 0 }
    floorSpots.value = []
    return
  }

  loadingFloorAvailability.value = true
  try {
    const res = await getSpacesByFloor(floor)
    const rows = Array.isArray(res?.data) ? res.data : (Array.isArray(res) ? res : [])
    floorSpots.value = rows

    let standard = 0
    let ev = 0

    rows.forEach((spot) => {
      const isAvailable = isSpotAvailable(spot)
      if (!isAvailable) return

      if (spot?.type) {
        ev += 1
      } else {
        standard += 1
      }
    })

    floorAvailability.value = {
      total: standard + ev,
      standard,
      ev,
    }

    if (reservationMode.value === 'specific' && reserveForm.spotId) {
      const selectedId = Number(reserveForm.spotId)
      const matched = specificSpotOptions.value.find((item) => item.id === selectedId)
      if (!matched) {
        reserveForm.spotId = null
        if (reserveForm.spotSpaceId) {
          ElMessage.warning(`指定车位 ${reserveForm.spotSpaceId.replace(/^space_/, '')} 当前不可预约，请重新选择`)
        }
        reserveForm.spotSpaceId = ''
      } else {
        reserveForm.spotSpaceId = matched.spaceId
      }
    }
  } catch (err) {
    floorAvailability.value = { total: 0, standard: 0, ev: 0 }
    floorSpots.value = []
    console.error('加载楼层可分配余量失败', err)
  } finally {
    loadingFloorAvailability.value = false
  }
}

onMounted(async () => {
  hasBankCard.value = hasBoundBankCard()
  const defaultMethod = getDefaultPaymentMethod('wechat')
  selectedPaymentMethod.value = (!hasBankCard.value && defaultMethod === 'card') ? 'wechat' : defaultMethod
  applyRoutePrefill()
  await loadPricingRules()
  await loadFloorOptions()
  await loadFloorAvailability()
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

  if (reservationMode.value === 'specific') {
    if (!reserveForm.spotId) {
      ElMessage.warning('请选择一个具体车位后再提交预约')
      return
    }
    if (!selectedSpecificSpot.value) {
      ElMessage.warning('该车位当前不可预约，请重新选择')
      return
    }
  } else if (selectedTypeAvailableCount.value <= 0) {
    ElMessage.warning('当前楼层该类型暂无可分配车位，请调整楼层或类型')
    return
  }

  await loadUserBalance()
  if (!isBalanceEnough.value && selectedPaymentMethod.value === 'balance') {
    selectedPaymentMethod.value = 'wechat'
  }

  showPaymentDialog.value = true
}

watch(
  () => reserveForm.floor,
  () => {
    loadFloorAvailability()
  }
)

watch(
  () => reserveForm.type,
  () => {
    if (reservationMode.value !== 'specific' || !reserveForm.spotId) return
    const selectedId = Number(reserveForm.spotId)
    const matched = specificSpotOptions.value.find((item) => item.id === selectedId)
    if (!matched) {
      reserveForm.spotId = null
      reserveForm.spotSpaceId = ''
    }
  }
)

watch(
  () => reservationMode.value,
  (mode) => {
    if (mode === 'random') {
      reserveForm.spotId = null
      reserveForm.spotSpaceId = ''
    }
  }
)

watch(
  () => reserveForm.spotId,
  (spotId) => {
    const selectedId = Number(spotId)
    const matched = specificSpotOptions.value.find((item) => item.id === selectedId)
    reserveForm.spotSpaceId = matched?.spaceId || ''
  }
)

function selectPaymentMethod(method) {
  if (method.disabled) {
    if (method.value === 'card') {
      ElMessage.warning('请先添加银行卡并完成验证')
      openAddBankCardDialog()
      return
    }
    ElMessage.warning('余额不足，请先充值后再使用余额支付')
    return
  }
  selectedPaymentMethod.value = method.value
}

function openAddBankCardDialog() {
  bankCardForm.value = {
    phone: '',
    holder: '',
    number: '',
    code: '',
  }
  bankCardHumanVerified.value = false
  resetBankCardPuzzleCaptcha()
  mockCardVerifyCode.value = ''
  showAddCardDialog.value = true
}

function resetBankCardPuzzleCaptcha() {
  bankCardHumanVerified.value = false
  bankCardPuzzleValue.value = 0
  bankCardPuzzleTarget.value = Math.floor(20 + Math.random() * (bankCardPuzzleMax - 40))
}

function handleBankCardPuzzleSlide() {
  if (bankCardHumanVerified.value) return
  const delta = Math.abs(Number(bankCardPuzzleValue.value || 0) - Number(bankCardPuzzleTarget.value || 0))
  if (delta <= 4) {
    bankCardHumanVerified.value = true
    ElMessage.success('人机验证通过')
  }
}

function requestBankCardCode() {
  const phone = String(bankCardForm.value.phone || '').trim()
  const holder = String(bankCardForm.value.holder || '').trim()
  const number = String(bankCardForm.value.number || '').replace(/\D/g, '')

  if (!bankCardHumanVerified.value) {
    ElMessage.warning('请先完成人机验证')
    return
  }

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

  mockCardVerifyCode.value = String(Math.floor(100000 + Math.random() * 900000))
  ElMessage.success(`验证码已发送（模拟）：${mockCardVerifyCode.value}`)
}

function confirmAddBankCard() {
  const phone = String(bankCardForm.value.phone || '').trim()
  const holder = String(bankCardForm.value.holder || '').trim()
  const number = String(bankCardForm.value.number || '').replace(/\D/g, '')
  const code = String(bankCardForm.value.code || '').trim()

  if (!/^1\d{10}$/.test(phone)) {
    ElMessage.warning('请输入正确的11位手机号')
    return
  }
  if (!bankCardHumanVerified.value) {
    ElMessage.warning('请先完成人机验证')
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
  if (!mockCardVerifyCode.value) {
    ElMessage.warning('请先获取验证码')
    return
  }
  if (code !== mockCardVerifyCode.value) {
    ElMessage.error('验证码错误，请重新输入')
    return
  }

  setBankCardBound(true)
  hasBankCard.value = true
  selectedPaymentMethod.value = 'card'
  bankCardForm.value = { phone: '', holder: '', number: '', code: '' }
  resetBankCardPuzzleCaptcha()
  showAddCardDialog.value = false
  ElMessage.success('银行卡已添加并验证成功')
}

async function submitReservation() {
  loading.value = true
  let balancePaid = false
  let balanceTxnId = ''
  try {
    if (selectedPaymentMethod.value === 'balance') {
      const payRes = await payWithBalance(totalFee.value, null, '预约车位费用')
      balancePaid = true
      balanceTxnId = String(payRes?.transaction_id || payRes?.data?.transaction_id || '')
    }

    const reservation = await createReservation({
      vehicle: reserveForm.vehicle,
      date: toDateString(new Date(reserveForm.date)),
      end_date: toDateString(new Date(reserveForm.endDate)),
      start_time: reserveForm.startTime,
      end_time: reserveForm.endTime,
      spot: reservationMode.value === 'specific' ? Number(reserveForm.spotId) : undefined,
      preferred_floor: reserveForm.floor,
      spot_type: reserveForm.type,
      payment_transaction_id: balanceTxnId,
      total_amount: totalFee.value,
      payment_method: selectedPaymentMethod.value
    })

    const floor = reservation?.spot_detail?.floor || reservation?.spot_floor || ''
    const spotId = reservation?.spot_detail?.spot_id || reservation?.spot_id || ''
    if (floor && spotId) {
      ElMessage.success(`预约成功，已分配车位：${floor}-${spotId}`)
    } else {
      ElMessage.success('预约成功，请准时入场！')
    }
    showPaymentDialog.value = false
    await loadUserBalance()
    router.push('/profile')
  } catch (err) {
    const responseData = err?.response?.data || {}
    const spotErrorRaw = responseData?.spot
    const spotError = Array.isArray(spotErrorRaw) ? String(spotErrorRaw[0] || '') : String(spotErrorRaw || '')
    const detail = String(responseData?.detail || '')
    if (selectedPaymentMethod.value === 'balance' && detail.includes('余额不足')) {
      ElMessage.error('余额不足，请先充值后再支付')
    } else if (spotError) {
      ElMessage.error(spotError)
    } else if (detail.includes('暂无可用车位')) {
      ElMessage.error(detail)
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

  hasBankCard.value = hasBoundBankCard()
  if (selectedPaymentMethod.value === 'card' && !hasBankCard.value) {
    ElMessage.warning('请先前往支付中心添加银行卡')
    router.push('/payment')
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
