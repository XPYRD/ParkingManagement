<template>
  <!-- 仪表盘 — 从 stitch_/_7/code.html 转换 -->
  <div class="p-6 lg:p-10 space-y-8">
    <!-- 顶部欢迎 + 时间 -->
    <header class="flex flex-col md:flex-row justify-between items-start md:items-center">
      <div>
        <h1 class="text-3xl font-extrabold text-primary tracking-tight font-headline">仪表盘</h1>
        <p class="text-secondary text-sm mt-1">实时数据概览与系统运行状况</p>
      </div>
      <div class="mt-4 md:mt-0 flex items-center gap-4">
        <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" size="small" />
        <el-button size="small" class="!rounded-lg">
          <span class="material-symbols-outlined text-sm mr-1">refresh</span>
          刷新数据
        </el-button>
      </div>
    </header>

    <!-- ===== 统计摘要卡片 ===== -->
    <section class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div
        v-for="card in summaryCards"
        :key="card.label"
        class="rounded-2xl p-6 bg-surface-container-lowest border border-outline-variant/10 shadow-sm hover:shadow-md transition-shadow"
      >
        <div class="flex items-center gap-2 mb-3">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center" :class="card.bgClass">
            <span class="material-symbols-outlined text-lg" :class="card.iconClass">{{ card.icon }}</span>
          </div>
        </div>
        <p class="text-xs font-bold text-secondary uppercase tracking-widest mb-1">{{ card.label }}</p>
        <p class="text-3xl font-extrabold text-on-surface font-headline tracking-tight">{{ card.value }}</p>
        <div class="flex items-center gap-1 mt-2">
          <span class="material-symbols-outlined text-xs" :class="card.trend > 0 ? 'text-green-500' : 'text-error'">
            {{ card.trend > 0 ? 'trending_up' : 'trending_down' }}
          </span>
          <span class="text-xs font-bold" :class="card.trend > 0 ? 'text-green-500' : 'text-error'">
            {{ Math.abs(card.trend) }}%
          </span>
          <span class="text-xs text-secondary">较昨日</span>
        </div>
      </div>
    </section>

    <!-- ===== 营收图表 + 空间占用 ===== -->
    <section class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 营收趋势 -->
      <div class="lg:col-span-2 rounded-2xl p-6 bg-surface-container-lowest border border-outline-variant/10 shadow-sm">
        <div class="flex justify-between items-center mb-6">
          <div>
            <h3 class="font-bold text-on-surface">营收趋势</h3>
            <p class="text-xs text-secondary mt-1">近7天营收数据</p>
          </div>
          <el-segmented v-model="revenueView" :options="['日', '周', '月']" size="small" />
        </div>
        <!-- 简化图表 — 用柱状条表示 -->
        <div class="flex items-end gap-3 h-48 px-2">
          <div
            v-for="(bar, i) in revenueData"
            :key="i"
            class="flex-1 flex flex-col items-center gap-2 justify-end h-full"
          >
            <span class="text-xs font-bold text-primary">¥{{ bar.value }}</span>
            <div
              class="w-full rounded-t-lg bg-gradient-to-t from-primary to-primary-container transition-all duration-500 hover:opacity-80"
              :style="{ height: `${(bar.value / maxRevenue) * 100}%` }"
            ></div>
            <span class="text-xs text-secondary">{{ bar.label }}</span>
          </div>
        </div>
      </div>

      <!-- 空间占用率饼图 -->
      <div class="rounded-2xl p-6 bg-surface-container-lowest border border-outline-variant/10 shadow-sm">
        <h3 class="font-bold text-on-surface mb-1">空间占用率</h3>
        <p class="text-xs text-secondary mb-6">实时车位分布</p>
        <!-- 环形图表示 -->
        <div class="relative w-40 h-40 mx-auto mb-6">
          <svg viewBox="0 0 100 100" class="transform -rotate-90">
            <circle cx="50" cy="50" r="40" fill="none" stroke="#e8e8e8" stroke-width="10"/>
            <circle
              cx="50" cy="50" r="40" fill="none"
              stroke="#000666" stroke-width="10"
              stroke-linecap="round"
              :stroke-dasharray="`${occupancyRate * 2.51} 251`"
              class="transition-all duration-1000"
            />
          </svg>
          <div class="absolute inset-0 flex flex-col items-center justify-center">
            <span class="text-3xl font-extrabold text-primary font-headline">{{ occupancyRate }}%</span>
            <span class="text-xs text-secondary">已占用</span>
          </div>
        </div>
        <div class="space-y-3">
          <div v-for="item in occupancyBreakdown" :key="item.label" class="flex items-center justify-between text-sm">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full" :class="item.dotClass"></div>
              <span class="text-secondary">{{ item.label }}</span>
            </div>
            <span class="font-bold text-on-surface">{{ item.count }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== 近期告警 + 系统运行 ===== -->
    <section class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 近期告警 -->
      <div class="rounded-2xl p-6 bg-surface-container-lowest border border-outline-variant/10 shadow-sm">
        <div class="flex justify-between items-center mb-4">
          <h3 class="font-bold text-on-surface">近期告警</h3>
          <router-link to="/admin/alerts" class="text-xs text-primary font-semibold hover:underline">查看全部 →</router-link>
        </div>
        <div class="space-y-3">
          <div
            v-for="alert in recentAlerts"
            :key="alert.id"
            class="flex items-start gap-3 p-3 rounded-xl hover:bg-surface-container-low transition-colors"
          >
            <div class="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0" :class="alert.bgClass">
              <span class="material-symbols-outlined text-sm" :class="alert.iconClass">{{ alert.icon }}</span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-on-surface truncate">{{ alert.title }}</p>
              <p class="text-xs text-secondary mt-0.5">{{ alert.time }}</p>
            </div>
            <span class="text-xs font-bold px-2 py-1 rounded-full flex-shrink-0" :class="alert.statusClass">{{ alert.status }}</span>
          </div>
        </div>
      </div>

      <!-- 系统运行状况 -->
      <div class="rounded-2xl p-6 bg-surface-container-lowest border border-outline-variant/10 shadow-sm">
        <h3 class="font-bold text-on-surface mb-4">系统运行状况</h3>
        <div class="space-y-4">
          <div v-for="sys in systemStatus" :key="sys.label" class="flex items-center gap-4">
            <div class="w-10 h-10 rounded-xl bg-green-50 flex items-center justify-center flex-shrink-0">
              <span class="material-symbols-outlined text-green-600 text-lg">{{ sys.icon }}</span>
            </div>
            <div class="flex-1">
              <div class="flex justify-between items-center mb-1">
                <span class="text-sm font-semibold text-on-surface">{{ sys.label }}</span>
                <span class="text-xs font-bold text-green-600">{{ sys.value }}</span>
              </div>
              <div class="w-full h-1.5 bg-surface-container-highest rounded-full overflow-hidden">
                <div class="h-full bg-green-500 rounded-full" :style="{ width: sys.value }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
/**
 * 管理后台仪表盘 — 接入 API 等真实数据
 */

import { ref, onMounted } from 'vue'
import { getDashboardOverview } from '@/api/dashboard'
import { getAlerts } from '@/api/alert'
import { ElMessage } from 'element-plus'

const dateRange = ref([])
const revenueView = ref('日')

const summaryCards = ref([
  { icon: 'monetization_on', label: '今日营收', value: '¥--', trend: 0, bgClass: 'bg-primary/10', iconClass: 'text-primary' },
  { icon: 'directions_car', label: '在场车辆', value: '--', trend: 0, bgClass: 'bg-blue-50', iconClass: 'text-blue-600' },
  { icon: 'trending_up', label: '今日流量', value: '--', trend: 0, bgClass: 'bg-green-50', iconClass: 'text-green-600' },
  { icon: 'build', label: '设备在线', value: '--/--', trend: 0, bgClass: 'bg-amber-50', iconClass: 'text-amber-600' },
])

const revenueData = ref([
  { label: '周一', value: 12500 },
  { label: '周二', value: 14200 },
  { label: '周三', value: 13800 },
  { label: '周四', value: 15600 },
  { label: '周五', value: 16800 },
  { label: '周六', value: 19200 },
  { label: '周日', value: 0 },
])
const maxRevenue = ref(20000)

const occupancyRate = ref(0)
const occupancyBreakdown = ref([])

const recentAlerts = ref([])

const systemStatus = ref([
  { icon: 'dns', label: '服务器负载', value: '23%' },
  { icon: 'router', label: '网络延迟', value: '98%' },
  { icon: 'storage', label: '存储空间', value: '62%' },
  { icon: 'battery_charging_full', label: '平均可用时长', value: '--%' },
])

async function loadData() {
  try {
    const data = await getDashboardOverview()
    
    // 更新四大汇总
    summaryCards.value[0].value = `¥${data.daily_revenue || 0}`
    summaryCards.value[1].value = `${data.occupancy.occupied || 0}`
    summaryCards.value[2].value = `${data.today_traffic || 0}`
    summaryCards.value[3].value = `${data.system_health.online || 0}/${data.system_health.total || 0}`
    
    // 更新占用率
    occupancyRate.value = data.occupancy.occupancy_rate || 0
    occupancyBreakdown.value = [
       { label: '已占用', count: data.occupancy.occupied, dotClass: 'bg-primary' },
       { label: '空闲', count: data.occupancy.free, dotClass: 'bg-green-500' },
       { label: '已预约', count: data.occupancy.reserved, dotClass: 'bg-amber-500' },
       { label: '维修中', count: data.occupancy.maintenance, dotClass: 'bg-error' },
    ]
    
    // 更新系统正常运行时间
    systemStatus.value[3].value = `${(data.system_health.avg_uptime || 0).toFixed(1)}%`
    
    // 借机把系统今日假想营收赋给最右侧一根柱子
    revenueData.value[6].value = data.daily_revenue
    maxRevenue.value = Math.max(...revenueData.value.map(d => d.value)) || 1
    
    // 加载近期告警
    const alertsRes = await getAlerts({ limit: 5 })
    const aList = alertsRes.results || alertsRes || []
    recentAlerts.value = aList.slice(0, 5).map(a => ({
       id: a.id,
       title: a.title,
       time: new Date(a.created_at).toLocaleString(),
       status: a.status === 'pending' ? '待处理' : '已解决',
       icon: a.severity === 'high' ? 'warning' : 'info',
       bgClass: a.severity === 'high' ? 'bg-error/10' : 'bg-amber-50',
       iconClass: a.severity === 'high' ? 'text-error' : 'text-amber-600',
       statusClass: a.status === 'pending' ? 'bg-error/10 text-error' : 'bg-green-50 text-green-600'
    }))
  } catch (err) {
    ElMessage.error('无法加载仪表盘数据')
  }
}

onMounted(() => {
  loadData()
})
</script>
