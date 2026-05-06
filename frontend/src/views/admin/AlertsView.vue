<template>
  <!-- 预警中心 -->
  <div class="px-6 lg:px-10 py-6 h-full flex flex-col items-center">
    <div class="w-full max-w-5xl flex flex-col h-full">
      <header class="flex justify-between items-end mb-8 flex-shrink-0">
        <div>
          <h1 class="text-3xl font-extrabold text-primary tracking-tight font-headline">安全预警中心</h1>
          <p class="text-secondary text-sm mt-1">全局异常监控、紧急事件处理与安防调度指挥</p>
        </div>
      </header>

      <!-- 顶部统计卡片 -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8 flex-shrink-0" v-loading="loadingStats">
        <div class="bg-surface-container-lowest p-5 rounded-2xl border-l-4 border-error shadow-sm flex flex-col justify-center">
          <p class="text-xs font-bold text-secondary uppercase tracking-widest mb-2">未处理威胁</p>
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-error text-3xl">warning</span>
            <span class="text-3xl font-black font-headline text-error">{{ stats.pending || 0 }}</span>
          </div>
        </div>
        <div class="bg-surface-container-lowest p-5 rounded-2xl border-l-4 border-amber-500 shadow-sm flex flex-col justify-center">
          <p class="text-xs font-bold text-secondary uppercase tracking-widest mb-2">高优先级告警</p>
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-amber-500 text-3xl">policy</span>
            <span class="text-3xl font-black font-headline text-amber-600">{{ stats.high_priority || 0 }}</span>
          </div>
        </div>
        <div class="bg-surface-container-lowest p-5 rounded-2xl border-l-4 border-primary shadow-sm flex flex-col justify-center">
          <p class="text-xs font-bold text-secondary uppercase tracking-widest mb-2">排查处理中</p>
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-primary text-3xl">my_location</span>
            <span class="text-3xl font-black font-headline text-primary">{{ stats.processing || 0 }}</span>
          </div>
        </div>
        <div class="bg-surface-container-lowest p-5 rounded-2xl border-l-4 border-green-500 shadow-sm flex flex-col justify-center">
          <p class="text-xs font-bold text-secondary uppercase tracking-widest mb-2">今日已解决</p>
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-green-500 text-3xl">gpp_good</span>
            <span class="text-3xl font-black font-headline text-green-600">{{ stats.resolved_today || 0 }}</span>
          </div>
        </div>
      </div>

      <!-- 预警事件 Feed 流 -->
      <div class="flex-1 bg-surface-container-lowest rounded-2xl border border-outline-variant/20 shadow-sm flex flex-col overflow-hidden">
        <div class="p-4 border-b border-outline-variant/20 flex gap-4 bg-surface-container-low/50">
          <el-radio-group v-model="filterPriority" size="small" @change="loadAlerts">
            <el-radio-button label="all">全部事件</el-radio-button>
            <el-radio-button label="high"><span class="text-error font-bold">高优先级</span></el-radio-button>
            <el-radio-button label="medium" class="text-amber-600">中优</el-radio-button>
          </el-radio-group>
        </div>

        <div class="flex-1 overflow-auto p-4 space-y-3" v-loading="loadingAlerts">
          <div 
             v-for="alert in alerts" 
             :key="alert.id"
             class="p-4 rounded-xl border flex flex-col md:flex-row md:items-center justify-between gap-4 transition-colors"
             :class="alert.severity === 'high' ? 'bg-error/5 border-error/30' : 'bg-surface border-outline-variant/20 hover:bg-surface-container-low'"
          >
            <div class="flex items-start gap-4">
              <!-- 图标 -->
              <div class="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0" :class="alert.severity==='high' ? 'bg-error' : 'bg-amber-500'">
                <span class="material-symbols-outlined text-2xl text-white">{{ alert.alert_type === 'security' ? 'security' : (alert.alert_type === 'device_fault' ? 'build' : 'warning') }}</span>
              </div>
              
              <!-- 内容 -->
              <div>
                <div class="flex items-center gap-2 mb-1">
                  <h3 class="font-bold text-on-surface text-base">{{ alert.title }}</h3>
                  <el-tag size="small" :type="alert.severity==='high'?'danger':(alert.severity==='medium'?'warning':'info')" effect="dark" class="!border-0 !rounded-md !px-1.5 !h-5 !text-[10px]">
                     {{ alert.severity_label || (alert.severity === 'high' ? '紧急' : '警告') }}
                  </el-tag>
                </div>
                <p class="text-sm text-secondary mb-2 max-w-2xl">{{ alert.description }}</p>
                <div class="flex items-center gap-4 text-xs font-semibold text-secondary">
                  <span class="flex items-center gap-1" v-if="alert.device_detail"><span class="material-symbols-outlined text-[14px]">location_on</span> {{ alert.device_detail.location || alert.device_detail.name }}</span>
                  <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[14px]">schedule</span> {{ new Date(alert.created_at).toLocaleString() }}</span>
                  <span class="flex items-center gap-1" v-if="alert.status === 'resolved'"><span class="material-symbols-outlined text-[14px] text-green-500">check_circle</span> 已解决</span>
                </div>
              </div>
            </div>

            <!-- 操作 -->
            <div class="flex items-center gap-2 md:flex-col lg:flex-row flex-shrink-0">
               <el-button v-if="alert.status === 'pending'" type="primary" size="small" @click="handleResolve(alert.id)">标记解决</el-button>
            </div>
          </div>
          
          <div v-if="alerts.length === 0" class="flex items-center justify-center p-12 text-secondary text-sm">
             暂无匹配的告警事件
          </div>
        </div>
        
         <div class="p-4 border-t border-outline-variant/20 flex justify-end">
            <el-pagination 
               v-model:current-page="currentPage" 
               size="small" 
               background 
               layout="total, prev, pager, next" 
               :total="totalAlerts" 
               @current-change="loadAlerts"
            />
         </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 预警中心后台 — 接入真实 API 数据
 */
import { ref, onMounted } from 'vue'
import { getAlerts, getAlertStats, resolveAlert } from '@/api/alert'
import { ElMessage } from 'element-plus'

const filterPriority = ref('all')

const stats = ref({})
const alerts = ref([])
const loadingStats = ref(false)
const loadingAlerts = ref(false)

const currentPage = ref(1)
const totalAlerts = ref(0)

onMounted(() => {
   loadStats()
   loadAlerts()
})

const loadStats = async () => {
   loadingStats.value = true
   try {
      const res = await getAlertStats()
      stats.value = res
   } catch(e) {
      console.error(e)
   } finally {
      loadingStats.value = false
   }
}

const loadAlerts = async () => {
   loadingAlerts.value = true
   try {
      const params = { page: currentPage.value }
      if (filterPriority.value !== 'all') {
         params.severity = filterPriority.value
      }
      const res = await getAlerts(params)
      if (res.results) {
         alerts.value = res.results
         totalAlerts.value = res.count
      } else {
         alerts.value = res
         totalAlerts.value = res.length
      }
   } catch(e) {
      ElMessage.error('无法加载告警列表')
   } finally {
      loadingAlerts.value = false
   }
}

const handleResolve = async (id) => {
   try {
      await resolveAlert(id)
      ElMessage.success('已标记解决')
      loadAlerts()
      loadStats()
   } catch(e) {
      ElMessage.error('操作失败')
   }
}
</script>
