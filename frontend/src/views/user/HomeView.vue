<template>
  <!-- 首页 — 从 stitch_/_1/code.html 转换 -->
  <div class="pb-8">
    <!-- ===== Hero Section ===== -->
    <section
      class="relative px-6 md:px-10 pt-8 pb-32 md:pb-24 bg-cover bg-center min-h-[420px] flex items-end rounded-b-3xl overflow-hidden mx-4 mt-2"
      :style="{ backgroundImage: `url(${heroImage})` }"
    >
      <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent"></div>
      <div class="relative z-10 max-w-2xl">
        <p class="text-white/70 text-sm font-bold uppercase tracking-[0.2em] mb-4">智能停车系统</p>
        <h1 class="text-4xl md:text-5xl font-extrabold text-white font-headline leading-tight tracking-tight mb-4">
          城市流动的<br/>智慧脉搏
        </h1>
        <p class="text-white/70 text-sm max-w-md leading-relaxed mb-6">
          体验下一代 AI 驱动的停车管理——实时监控每一个车位、预测流量峰值、优化空间利用率。
        </p>
        <div class="flex gap-3">
          <router-link to="/map">
            <el-button type="primary" size="large" class="!rounded-full !px-6 !font-bold !shadow-lg">
              查看实时车位
            </el-button>
          </router-link>
          <router-link to="/reserve">
            <el-button size="large" class="!rounded-full !px-6 !font-bold !bg-white/15 !backdrop-blur-md !text-white !border-white/20 hover:!bg-white/25">
              预约停车
            </el-button>
          </router-link>
        </div>
      </div>
    </section>

    <!-- ===== 实时统计 Bento 网格 ===== -->
    <section class="px-6 md:px-10 -mt-16 relative z-20 max-w-7xl mx-auto">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div
          v-for="stat in statsCards"
          :key="stat.label"
          class="glass-panel rounded-2xl p-5 shadow-lg border border-white/30 hover:shadow-xl hover:-translate-y-0.5 transition-all duration-300"
        >
          <div class="flex items-center gap-2 mb-3">
            <span class="material-symbols-outlined text-primary text-xl">{{ stat.icon }}</span>
            <span class="text-xs font-bold text-secondary uppercase tracking-widest">{{ stat.label }}</span>
          </div>
          <p class="text-3xl font-extrabold text-on-surface font-headline tracking-tight">{{ stat.value }}</p>
          <p class="text-xs text-secondary mt-1">{{ stat.desc }}</p>
        </div>
      </div>
    </section>

    <!-- ===== 免登录快速缴费（大区块） ===== -->
    <section class="px-6 md:px-10 mt-12 max-w-7xl mx-auto">
      <div class="rounded-3xl overflow-hidden shadow-2xl border border-primary/10 bg-gradient-to-br from-[#0b3a6f] via-[#0f5ca8] to-[#27a2b8]">
        <div class="grid grid-cols-1 lg:grid-cols-2">
          <div class="p-8 md:p-12 text-white relative">
            <div class="absolute right-6 top-6 text-xs font-black tracking-widest px-3 py-1 rounded-full bg-white/20">免登录</div>
            <p class="text-white/70 text-xs font-bold tracking-[0.18em] uppercase mb-4">Quick Pay Express</p>
            <h2 class="text-3xl md:text-4xl font-black leading-tight font-headline mb-4">快速缴费通道</h2>
            <p class="text-white/85 text-sm md:text-base leading-relaxed max-w-lg">
              车主无需登录，输入车牌即可快速发起缴费。支持微信、支付宝、银行卡扫码支付。
            </p>
            <div class="mt-8 flex flex-wrap gap-3 text-xs">
              <span class="px-3 py-1 rounded-full bg-white/15">无需账号</span>
              <span class="px-3 py-1 rounded-full bg-white/15">30秒完成</span>
              <span class="px-3 py-1 rounded-full bg-white/15">安全支付</span>
            </div>
          </div>

          <div class="p-8 md:p-10 bg-white/95">
            <el-form label-position="top" class="space-y-3">
              <el-form-item label="车牌来源">
                <el-radio-group v-model="plateSourceMode" class="!flex gap-2 !w-full">
                  <el-radio-button label="manual" class="flex-1 text-center">手动输入</el-radio-button>
                  <el-radio-button label="my_vehicle" class="flex-1 text-center">我的车辆</el-radio-button>
                </el-radio-group>
              </el-form-item>

              <el-form-item v-if="plateSourceMode === 'my_vehicle'" label="选择我的车辆">
                <el-select
                  v-model="selectedVehicleId"
                  size="large"
                  placeholder="请选择已绑定车辆"
                  class="w-full"
                  filterable
                  clearable
                >
                  <el-option
                    v-for="car in myVehicles"
                    :key="car.id"
                    :label="car.plate_number"
                    :value="car.id"
                  />
                </el-select>
                <p v-if="!myVehicles.length" class="mt-2 text-xs text-slate-500">
                  当前账号暂无已绑定车辆，可切换到手动输入。
                </p>
              </el-form-item>

              <el-form-item label="车牌号">
                <el-input
                  v-model="quickPayForm.plate_number"
                  size="large"
                  placeholder="支持键盘输入/粘贴，或点击展开小键盘"
                  :disabled="plateSourceMode === 'my_vehicle'"
                  @click="plateSourceMode === 'manual' ? (plateKeyboardVisible = true) : null"
                  @focus="plateSourceMode === 'manual' ? (plateKeyboardVisible = true) : null"
                  @input="handleQuickPayPlateInput"
                  @paste="handleQuickPayPlatePaste"
                />
              </el-form-item>

              <div v-if="plateSourceMode === 'manual' && plateKeyboardVisible" class="rounded-2xl border border-slate-200 bg-slate-50 p-3 md:p-4">
                <div class="flex items-center justify-between mb-3">
                  <p class="text-xs font-bold tracking-widest text-slate-500">车牌小键盘</p>
                  <el-button link type="primary" @click="plateKeyboardVisible = false">收起</el-button>
                </div>

                <el-form label-position="top">
                  <el-form-item label="能源类型">
                    <el-radio-group v-model="quickPayForm.energy_type" class="!flex gap-2">
                      <el-radio-button label="ice">油车（蓝牌）</el-radio-button>
                      <el-radio-button label="new_energy">新能源（绿牌）</el-radio-button>
                    </el-radio-group>
                  </el-form-item>
                </el-form>

                <div class="max-h-[340px] overflow-y-auto pr-1">
                  <PlateNumberInput
                    v-model="quickPayForm.plate_number"
                    :energy-type="quickPayForm.energy_type"
                    @complete="handleQuickPayPlateComplete"
                  />
                </div>
              </div>

              <el-form-item>
                <el-button
                  size="large"
                  class="!w-full !h-12 !font-bold"
                  :loading="quickPayQuoteLoading"
                  @click="queryQuickPayQuote"
                >
                  查询停车时长与费用
                </el-button>
              </el-form-item>

              <div v-if="quickPayQuote" class="rounded-2xl border border-primary/20 bg-primary/5 p-4 space-y-2">
                <div class="flex justify-between text-sm text-slate-600">
                  <span>已停时长</span>
                  <span class="font-bold text-slate-800">{{ quickPayQuote.duration_text }}</span>
                </div>
                <div class="flex justify-between text-sm text-slate-600">
                  <span>计费小时</span>
                  <span class="font-bold text-slate-800">{{ quickPayQuote.chargeable_hours }} 小时</span>
                </div>
                <div class="flex justify-between text-sm text-slate-600">
                  <span>当前应缴</span>
                  <span class="font-black text-lg text-primary">¥ {{ quickPayQuote.amount }}</span>
                </div>
                <p v-if="quickPayQuote.leave_tip" class="text-xs text-amber-600 font-semibold">
                  {{ quickPayQuote.leave_tip }}
                </p>
              </div>

              <el-form-item label="支付方式">
                <el-radio-group v-model="quickPayForm.method" class="!flex gap-2 !w-full">
                  <el-radio-button label="wechat" class="flex-1 text-center">
                    <span class="inline-flex items-center gap-1">
                      <img src="/微信支付.svg" alt="微信支付" class="w-4 h-4 object-contain" />
                      <span>微信</span>
                    </span>
                  </el-radio-button>
                  <el-radio-button label="alipay" class="flex-1 text-center">
                    <span class="inline-flex items-center gap-1">
                      <img src="/支付宝支付.svg" alt="支付宝支付" class="w-4 h-4 object-contain" />
                      <span>支付宝</span>
                    </span>
                  </el-radio-button>
                  <el-radio-button label="card" class="flex-1 text-center" :disabled="!hasBankCard">
                    <span class="inline-flex items-center gap-1">
                      <img src="/银行卡.svg" alt="银行卡支付" class="w-4 h-4 object-contain" />
                      <span>银行卡</span>
                    </span>
                  </el-radio-button>
                </el-radio-group>
                <p v-if="!hasBankCard" class="mt-2 text-xs text-slate-500">
                  暂未添加银行卡，
                  <router-link to="/payment" class="text-primary hover:underline">前往支付中心添加</router-link>
                </p>
              </el-form-item>

              <el-button
                type="primary"
                size="large"
                class="!w-full !h-12 !font-extrabold !text-base"
                :loading="quickPayLoading"
                :disabled="!quickPayQuote || Number(quickPayQuote.amount || 0) <= 0"
                @click="submitQuickPay"
              >
                {{ quickPayQuote ? (Number(quickPayQuote.amount || 0) > 0 ? '立即支付' : '已缴费待出场') : '请先查询' }}
              </el-button>
            </el-form>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== 车辆进出场模拟（独立区块） ===== -->
    <section class="px-6 md:px-10 mt-8 max-w-7xl mx-auto">
      <div class="rounded-3xl border border-slate-200 bg-white p-6 md:p-8 shadow-lg">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-lg font-bold text-on-surface tracking-tight font-headline">车辆进出场模拟</h2>
          <p class="text-xs text-slate-500">使用上方当前车牌进行模拟</p>
        </div>

        <el-tabs v-model="simulationTab" class="simulation-tabs">
          <el-tab-pane label="车辆进场模拟" name="entry">
            <div class="pt-2 space-y-3">
              <el-form label-position="top" class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <el-form-item label="车牌来源" class="md:col-span-2">
                  <el-radio-group v-model="entryPlateSourceMode" class="!flex gap-2 !w-full">
                    <el-radio-button label="manual" class="flex-1 text-center">手动输入</el-radio-button>
                    <el-radio-button label="my_vehicle" class="flex-1 text-center">绑定车辆</el-radio-button>
                    <el-radio-button label="image" class="flex-1 text-center">上传识别</el-radio-button>
                  </el-radio-group>
                </el-form-item>

                <el-form-item v-if="entryPlateSourceMode === 'my_vehicle'" label="选择绑定车辆" class="md:col-span-2">
                  <el-select
                    v-model="entryVehicleId"
                    placeholder="请选择已绑定车辆"
                    class="w-full"
                    filterable
                    clearable
                  >
                    <el-option
                      v-for="car in myVehicles"
                      :key="car.id"
                      :label="car.plate_number"
                      :value="car.id"
                    />
                  </el-select>
                </el-form-item>

                <el-form-item v-if="entryPlateSourceMode === 'image'" label="上传车辆图片" class="md:col-span-2">
                  <div class="w-full flex flex-wrap gap-2 items-center">
                    <input type="file" accept="image/*" @change="handleEntryImageChange" />
                    <el-button :loading="entryRecognitionLoading" @click="recognizeEntryPlateFromImage">自动识别车牌</el-button>
                    <span v-if="entryImageName" class="text-xs text-slate-500">已选: {{ entryImageName }}</span>
                  </div>
                </el-form-item>

                <el-form-item label="车牌号" class="md:col-span-1">
                  <el-input
                    v-model="entrySimulationPlate"
                    placeholder="请输入或识别车牌号"
                    :disabled="entryPlateSourceMode === 'my_vehicle'"
                    @input="handleEntrySimulationPlateInput"
                  />
                </el-form-item>

                <el-form-item label="停车楼层" class="md:col-span-1">
                  <el-select v-model="entrySimulationFloor" placeholder="请选择楼层" class="w-full">
                    <el-option label="B2 地下二层" value="B2" />
                    <el-option label="B1 地下一层" value="B1" />
                    <el-option label="1F 一楼" value="1F" />
                  </el-select>
                </el-form-item>
              </el-form>

              <el-button
                size="large"
                class="!w-full md:!w-auto !h-12 !font-bold"
                :loading="markEntryLoading"
                @click="simulateVehicleEntry"
              >
                车辆进场(模拟)
              </el-button>
              <p class="text-xs text-slate-500">系统会在所选楼层随机分配可用车位，并提示分配位置。</p>
            </div>
          </el-tab-pane>
          <el-tab-pane label="车辆出场模拟" name="exit">
            <div class="pt-2 space-y-2">
              <el-button
                size="large"
                class="!w-full md:!w-auto !h-12 !font-bold"
                :loading="markExitLoading"
                :disabled="!quickPayQuote || !quickPayQuote.session_id"
                @click="simulateVehicleExit"
              >
                车辆已出场(模拟)
              </el-button>
              <p class="text-xs text-slate-500">需先查询到在场记录后，才可模拟出场。</p>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </section>

    <!-- ===== 快速操作 ===== -->
    <section class="px-6 md:px-10 mt-12 max-w-7xl mx-auto">
      <h2 class="text-lg font-bold text-on-surface tracking-tight mb-6 font-headline">快速操作</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <router-link
          v-for="action in quickActions"
          :key="action.path"
          :to="action.path"
          class="group flex flex-col items-center gap-3 p-6 rounded-2xl bg-surface-container-low hover:bg-primary hover:text-white transition-all duration-300 cursor-pointer shadow-sm hover:shadow-lg hover:-translate-y-1"
        >
          <span class="material-symbols-outlined text-3xl text-primary group-hover:text-white transition-colors">{{ action.icon }}</span>
          <span class="text-sm font-bold group-hover:text-white transition-colors">{{ action.label }}</span>
          <span class="text-xs text-secondary group-hover:text-white/70 transition-colors text-center">{{ action.desc }}</span>
        </router-link>
      </div>
    </section>

    <!-- ===== 停车场状态预览 ===== -->
    <section class="px-6 md:px-10 mt-12 max-w-7xl mx-auto">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-lg font-bold text-on-surface tracking-tight font-headline">停车场状态</h2>
        <router-link to="/map" class="text-sm text-primary font-semibold hover:underline">查看详细地图 →</router-link>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div
          v-for="floor in floorPreview"
          :key="floor.name"
          class="rounded-2xl p-6 bg-surface-container-low border border-outline-variant/10 hover:shadow-md transition-shadow"
        >
          <div class="flex justify-between items-center mb-4">
            <h3 class="font-bold text-on-surface">{{ floor.name }}</h3>
            <span
              class="text-xs font-bold px-3 py-1 rounded-full"
              :class="floor.rate > 90 ? 'bg-error/10 text-error' : floor.rate > 70 ? 'bg-amber-50 text-amber-600' : 'bg-green-50 text-green-600'"
            >
              {{ floor.rate }}% 占用
            </span>
          </div>
          <!-- 占用率进度条 -->
          <div class="w-full h-2.5 bg-surface-container-highest rounded-full overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-700"
              :class="floor.rate > 90 ? 'bg-error' : floor.rate > 70 ? 'bg-amber-500' : 'bg-green-500'"
              :style="{ width: `${floor.rate}%` }"
            ></div>
          </div>
          <div class="flex justify-between mt-3 text-xs text-secondary">
            <span>空闲 {{ floor.free }} 个</span>
            <span>总计 {{ floor.total }} 个</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== 联系信息 ===== -->
    <section class="px-6 md:px-10 mt-12 max-w-7xl mx-auto">
      <div class="rounded-2xl bg-primary p-8 md:p-12 text-white">
        <h2 class="text-2xl font-extrabold font-headline tracking-tight mb-2">需要帮助？</h2>
        <p class="text-white/70 text-sm mb-6 max-w-md">24小时客户服务热线已为您准备就绪。我们的专业团队随时解答您的停车问题。</p>
        <div class="flex flex-wrap gap-6">
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-white/70">call</span>
            <span class="font-bold">400-888-0000</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-white/70">mail</span>
            <span class="font-bold">support@sentinel.com</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-white/70">location_on</span>
            <span class="font-bold">北京市朝阳区科技路88号</span>
          </div>
        </div>
      </div>
    </section>
    <el-dialog v-model="quickPayDialogVisible" title="请扫码完成支付" width="92%" max-width="460px">
      <div class="text-center">
        <img :src="quickPayResult.qr_code_url" alt="快速缴费二维码" class="w-56 h-56 mx-auto rounded-xl border border-slate-200" />
        <p class="mt-4 text-sm text-slate-700">车牌：{{ quickPayResult.plate_number }}</p>
        <p class="mt-1 text-lg font-black text-primary">¥ {{ quickPayResult.amount }}</p>
        <p class="mt-2 text-xs text-slate-500">交易号：{{ quickPayResult.transaction_id }}</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="confirmQuickPayPaid">我已支付（模拟）</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
/**
 * 首页 — 接入实际 API 数据
 */

import { ref, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getParkingSpaceStatistics, getSpacesByFloor, sendWebhookEvent, recognizePlateFromImage } from '@/api/parking'
import { quickPayNoLogin, quickPayQuoteNoLogin, quickPayMarkExit } from '@/api/payment'
import { getVehicles } from '@/api/user'
import PlateNumberInput from '@/components/PlateNumberInput.vue'
import heroImage from '@/assets/images/hero_bg.png'
import { hasBoundBankCard } from '@/utils/bankCard'
import { getDefaultPaymentMethod } from '@/utils/paymentPreference'

import { usePlateStore } from '@/stores/plate'
/** 实时统计卡片 */
const statsCards = ref([
  { icon: 'local_parking', label: '可用车位', value: '--', desc: '实时更新' },
  { icon: 'directions_car', label: '在场车辆', value: '--', desc: '总占有' },
  { icon: 'event_available', label: '已预约', value: '--', desc: '预约锁定' },
  { icon: 'build', label: '维修中', value: '--', desc: '暂不可用' },
])

const quickActions = [
  { path: '/map', icon: 'map', label: '查看地图', desc: '实时车位状态' },
  { path: '/map', icon: 'search', label: '车牌找车位', desc: '地图页顶部直接搜索' },
  { path: '/reserve', icon: 'event', label: '预约车位', desc: '提前锁定位置' },
  { path: '/payment', icon: 'credit_card', label: '在线支付', desc: '快速缴费离场' },
]

const floorPreview = ref([])
let refreshTimer = null
const plateStore = usePlateStore()

const quickPayLoading = ref(false)
const markEntryLoading = ref(false)
const markExitLoading = ref(false)
const quickPayQuoteLoading = ref(false)
const quickPayDialogVisible = ref(false)
const plateKeyboardVisible = ref(false)
const simulationTab = ref('entry')
const plateSourceMode = ref('manual')
const myVehicles = ref([])
const selectedVehicleId = ref(null)
const hasBankCard = ref(false)
const entryPlateSourceMode = ref('manual')
const entryVehicleId = ref(null)
const entrySimulationPlate = ref('')
const entrySimulationFloor = ref('B2')
const entryImageFile = ref(null)
const entryImageName = ref('')
const entryRecognitionLoading = ref(false)
const quickPayForm = ref({
  plate_number: '',
  energy_type: 'ice',
  method: 'wechat',
})
const quickPayQuote = ref(null)
const quickPayResult = ref({
  qr_code_url: '',
  plate_number: '',
  amount: '0.00',
  transaction_id: '',
})

async function submitQuickPay() {
  if (!quickPayQuote.value) {
    ElMessage.warning('请先查询停车费用')
    return
  }

  hasBankCard.value = hasBoundBankCard()
  if (quickPayForm.value.method === 'card' && !hasBankCard.value) {
    ElMessage.warning('请先前往支付中心添加银行卡')
    return
  }

  const plate = getCurrentPlateNumber()
  if (!plate) {
    ElMessage.warning('请输入车牌号')
    return
  }

  quickPayLoading.value = true
  try {
    const res = await quickPayNoLogin(
      plate,
      quickPayQuote.value.amount,
      quickPayForm.value.method,
      quickPayQuote.value.session_id,
    )

    if (res?.payment_state === 'subscription_free') {
      ElMessage.success(res?.leave_tip || '当前订阅有效，车辆进出场免费，无需支付')
      quickPayDialogVisible.value = false
      await queryQuickPayQuote(false)
      return
    }

    quickPayResult.value = {
      qr_code_url: res?.qr_code_url || '',
      plate_number: res?.plate_number || plate,
      amount: res?.amount || String(quickPayQuote.value.amount),
      transaction_id: res?.transaction_id || '',
    }
    quickPayDialogVisible.value = true
  } catch (err) {
    console.error('快速缴费失败', err)
  } finally {
    quickPayLoading.value = false
  }
}

async function simulateVehicleExit() {
  if (!quickPayQuote.value?.session_id) {
    ElMessage.warning('请先查询在场车辆')
    return
  }

  const plate = getCurrentPlateNumber()
  markExitLoading.value = true
  try {
    await quickPayMarkExit(plate, quickPayQuote.value.session_id)
    ElMessage.success('已模拟车辆出场')
    quickPayQuote.value = null
    await queryQuickPayQuote(false)
  } catch (err) {
    console.error('模拟出场失败', err)
  } finally {
    markExitLoading.value = false
  }
}

function isSpotAvailableForEntry(spot) {
  const isDamaged = Boolean(spot?.is_damaged)
  const isReserved = Boolean(String(spot?.reserved_plate || '').trim())
  const hasCurrentPlate = Boolean(String(spot?.current_plate || '').trim())
  return !isDamaged && !isReserved && !hasCurrentPlate
}

async function pickRandomAvailableSpot(preferredFloor = '') {
  const floors = preferredFloor ? [preferredFloor] : ['B2', 'B1', '1F']

  for (const floor of floors) {
    const res = await getSpacesByFloor(floor)
    const rows = Array.isArray(res?.data) ? res.data : (Array.isArray(res) ? res : [])
    const candidates = rows.filter(isSpotAvailableForEntry)
    if (candidates.length > 0) {
      const randomIndex = Math.floor(Math.random() * candidates.length)
      return candidates[randomIndex]
    }
  }

  return null
}

function normalizePlate(value) {
  return String(value || '').toUpperCase().replace(/\s+/g, '').trim()
}

function handleEntrySimulationPlateInput(value) {
  entrySimulationPlate.value = normalizePlate(value)
}

function getEntrySimulationPlate() {
  if (entryPlateSourceMode.value === 'my_vehicle') {
    const selectedVehicle = myVehicles.value.find((car) => Number(car.id) === Number(entryVehicleId.value))
    return normalizePlate(selectedVehicle?.plate_number || '')
  }
  return normalizePlate(entrySimulationPlate.value)
}

function handleEntryImageChange(event) {
  const file = event?.target?.files?.[0]
  if (!file) {
    entryImageFile.value = null
    entryImageName.value = ''
    return
  }
  entryImageFile.value = file
  entryImageName.value = file.name
}

function extractPlateFromRecognizeResult(res) {
  const candidates = [
    res?.plate_number,
    res?.license_plate,
    res?.data?.plate_number,
    res?.data?.license_plate,
    Array.isArray(res?.results) && res.results.length ? res.results[0]?.plate_number : '',
    Array.isArray(res?.detections) && res.detections.length ? res.detections[0]?.plate_number : '',
  ]
  const matched = candidates.find((item) => normalizePlate(item))
  return normalizePlate(matched || '')
}

async function recognizeEntryPlateFromImage() {
  if (entryPlateSourceMode.value !== 'image') {
    ElMessage.warning('请切换到上传识别模式')
    return
  }
  if (!entryImageFile.value) {
    ElMessage.warning('请先选择图片')
    return
  }

  entryRecognitionLoading.value = true
  try {
    const res = await recognizePlateFromImage(entryImageFile.value, 'entry')
    const plate = extractPlateFromRecognizeResult(res)
    if (!plate) {
      ElMessage.warning('未识别到车牌，请重试或手动输入')
      return
    }
    entrySimulationPlate.value = plate
    ElMessage.success(`识别成功：${plate}`)
  } catch (err) {
    console.error('图片识别失败', err)
    ElMessage.error('图片识别失败，请稍后重试')
  } finally {
    entryRecognitionLoading.value = false
  }
}

async function simulateVehicleEntry() {
  const plate = getEntrySimulationPlate()
  if (!plate) {
    ElMessage.warning('请先选择或输入车牌号')
    return
  }

  markEntryLoading.value = true
  try {
    let quote = null
    try {
      quote = await quickPayQuoteNoLogin(plate)
    } catch (quoteErr) {
      const code = Number(quoteErr?.response?.status || 0)
      if (![400, 404].includes(code)) {
        throw quoteErr
      }
    }

    if (quote?.found !== false) {
      quickPayQuote.value = {
        session_id: quote?.session_id,
        duration_text: quote?.duration_text || '--',
        chargeable_hours: quote?.chargeable_hours ?? 0,
        amount: quote?.amount || '0.00',
        payment_state: quote?.payment_state || 'charging',
        leave_tip: quote?.leave_tip || '',
      }
      ElMessage.warning('该车辆已在场，无需重复入场')
      return
    }

    const targetSpot = await pickRandomAvailableSpot(entrySimulationFloor.value)
    if (!targetSpot?.space_id) {
      ElMessage.error(`所选楼层 ${entrySimulationFloor.value} 无可用车位，无法模拟入场`)
      return
    }

    await sendWebhookEvent({
      event_type: 'space_occupied',
      space_id: targetSpot.space_id,
      plate_number: plate,
      timestamp: new Date().toISOString(),
    })

    const displaySpotId = String(targetSpot.space_id || '').replace(/^space_/, '')
    const displayFloor = targetSpot.floor || entrySimulationFloor.value || '--'
    ElMessage.success(`已模拟车辆入场，随机分配车位：${displayFloor}-${displaySpotId}`)

    plateSourceMode.value = 'manual'
    quickPayForm.value.plate_number = plate
    plateStore.setPlateNumber(plate)
    await Promise.all([
      loadHomeStats(),
      queryQuickPayQuote(false),
    ])
  } catch (err) {
    console.error('模拟入场失败', err)
    ElMessage.error('模拟入场失败，请稍后重试')
  } finally {
    markEntryLoading.value = false
  }
}

async function confirmQuickPayPaid() {
  quickPayDialogVisible.value = false
  await queryQuickPayQuote(false)
  ElMessage.success('已模拟扫码支付成功')
}

async function queryQuickPayQuote(showToast = true) {
  const plate = getCurrentPlateNumber()
  if (!plate) {
    ElMessage.warning('请输入车牌号')
    return
  }

  quickPayQuoteLoading.value = true
  quickPayQuote.value = null
  try {
    const res = await quickPayQuoteNoLogin(plate)
    if (res?.found === false) {
      if (showToast) {
        ElMessage.warning(res?.detail || '未找到该车牌在场停车记录')
      }
      return
    }

    quickPayQuote.value = {
      session_id: res?.session_id,
      duration_text: res?.duration_text || '--',
      chargeable_hours: res?.chargeable_hours ?? 0,
      amount: res?.amount || '0.00',
      payment_state: res?.payment_state || 'charging',
      leave_tip: res?.leave_tip || '',
    }
    if (showToast) {
      ElMessage.success('已查询到当前停车费用')
    }
  } catch (err) {
    console.error('查询停车费用失败', err)
  } finally {
    quickPayQuoteLoading.value = false
  }
}

async function handleQuickPayPlateComplete(plateNumber) {
  quickPayForm.value.plate_number = String(plateNumber || '').trim().toUpperCase()
  plateStore.setPlateNumber(quickPayForm.value.plate_number)
  plateKeyboardVisible.value = false
  await queryQuickPayQuote(false)
}

function getCurrentPlateNumber() {
  const selectedVehicle = myVehicles.value.find((car) => Number(car.id) === Number(selectedVehicleId.value))
  if (plateSourceMode.value === 'my_vehicle' && selectedVehicle?.plate_number) {
    const normalized = String(selectedVehicle.plate_number).trim().toUpperCase()
    quickPayForm.value.plate_number = normalized
    return normalized
  }

  return String(quickPayForm.value.plate_number || '').trim().toUpperCase()
}

function handleQuickPayPlateInput(value) {
  const normalized = String(value || '').toUpperCase().replace(/\s+/g, '')
  if (normalized !== quickPayForm.value.plate_number) {
    quickPayForm.value.plate_number = normalized
  }
  plateStore.setPlateNumber(normalized)
}

function handleQuickPayPlatePaste(event) {
  event?.preventDefault?.()
  const pasted = event?.clipboardData?.getData('text') || ''
  if (!pasted) {
    return
  }
  const normalized = String(pasted).toUpperCase().replace(/\s+/g, '')
  quickPayForm.value.plate_number = normalized
  plateStore.setPlateNumber(normalized)
}

async function loadHomeStats() {
  try {
    const res = await getParkingSpaceStatistics()
    const floorStats = res?.data || {}

    const mapped = Object.entries(floorStats).map(([floor, stat]) => {
      const total = Number(stat.total || 0)
      const occupied = Number(stat.occupied || 0)
      const free = Number(stat.free_regular || 0) + Number(stat.free_charging || 0)
      const rate = total > 0 ? Math.round((occupied / total) * 100) : 0

      return {
        name: floor === '1F' ? '地面层 (1F)' : `地下一层 (${floor})`,
        rate,
        free,
        total,
      }
    })
    floorPreview.value = mapped

    let totalFree = 0
    let totalOccupied = 0
    let totalReserved = 0
    let totalMaintenance = 0

    Object.values(floorStats).forEach((f) => {
      totalFree += Number(f.free_regular || 0) + Number(f.free_charging || 0)
      totalOccupied += Number(f.occupied || 0)
      totalReserved += Number(f.reserved || 0)
      totalMaintenance += Number(f.maintenance || 0)
    })

    statsCards.value[0].value = totalFree.toString()
    statsCards.value[1].value = totalOccupied.toString()
    statsCards.value[2].value = totalReserved.toString()
    statsCards.value[3].value = totalMaintenance.toString()
  } catch (err) {
    console.error('Failed to load floor summary', err)
  }
}

onMounted(async () => {
  hasBankCard.value = hasBoundBankCard()
  const defaultMethod = getDefaultPaymentMethod('wechat')
  quickPayForm.value.method = (!hasBankCard.value && defaultMethod === 'card') ? 'wechat' : defaultMethod
  if (plateStore.plateNumber) {
    quickPayForm.value.plate_number = plateStore.plateNumber
  }
  try {
    const res = await getVehicles()
    myVehicles.value = Array.isArray(res?.results) ? res.results : (Array.isArray(res) ? res : [])
    if (myVehicles.value.length > 0) {
      entryVehicleId.value = myVehicles.value[0].id
    }
  } catch (err) {
    myVehicles.value = []
  }
  await loadHomeStats()
  refreshTimer = window.setInterval(loadHomeStats, 30000)
})

watch(
  () => hasBankCard.value,
  (bound) => {
    if (!bound && quickPayForm.value.method === 'card') {
      quickPayForm.value.method = 'wechat'
    }
  },
)

onUnmounted(() => {
  if (refreshTimer) {
    window.clearInterval(refreshTimer)
    refreshTimer = null
  }
})

watch(
  () => quickPayForm.value.plate_number,
  (val) => {
    if (plateSourceMode.value === 'manual') {
      plateStore.setPlateNumber(val)
    }
    quickPayQuote.value = null
  },
)

watch(
  () => plateSourceMode.value,
  (mode) => {
    quickPayQuote.value = null
    if (mode === 'manual') {
      if (plateStore.plateNumber && !quickPayForm.value.plate_number) {
        quickPayForm.value.plate_number = plateStore.plateNumber
      }
      return
    }

    plateKeyboardVisible.value = false
    const selectedVehicle = myVehicles.value.find((car) => Number(car.id) === Number(selectedVehicleId.value))
    quickPayForm.value.plate_number = selectedVehicle?.plate_number
      ? String(selectedVehicle.plate_number).trim().toUpperCase()
      : ''
  },
)

watch(
  () => selectedVehicleId.value,
  (vehicleId) => {
    if (plateSourceMode.value !== 'my_vehicle') return
    const selectedVehicle = myVehicles.value.find((car) => Number(car.id) === Number(vehicleId))
    quickPayForm.value.plate_number = selectedVehicle?.plate_number
      ? String(selectedVehicle.plate_number).trim().toUpperCase()
      : ''
    quickPayQuote.value = null
  },
)

watch(
  () => plateStore.plateNumber,
  (val) => {
    if (plateSourceMode.value !== 'manual') return
    if (val !== quickPayForm.value.plate_number) {
      quickPayForm.value.plate_number = val
    }
  },
)

watch(
  () => entryPlateSourceMode.value,
  (mode) => {
    if (mode === 'my_vehicle') {
      const selectedVehicle = myVehicles.value.find((car) => Number(car.id) === Number(entryVehicleId.value))
      entrySimulationPlate.value = normalizePlate(selectedVehicle?.plate_number || '')
      return
    }
    if (mode === 'image') {
      entrySimulationPlate.value = ''
      return
    }
    if (mode === 'manual' && plateStore.plateNumber && !entrySimulationPlate.value) {
      entrySimulationPlate.value = normalizePlate(plateStore.plateNumber)
    }
  },
)

watch(
  () => entryVehicleId.value,
  (vehicleId) => {
    if (entryPlateSourceMode.value !== 'my_vehicle') return
    const selectedVehicle = myVehicles.value.find((car) => Number(car.id) === Number(vehicleId))
    entrySimulationPlate.value = normalizePlate(selectedVehicle?.plate_number || '')
  },
)
</script>
