<template>
  <!-- 设备网络管理 -->
  <div class="p-6 lg:p-10 h-full flex flex-col">
    <header class="flex justify-between items-end mb-8 flex-shrink-0">
      <div>
        <h1 class="text-3xl font-extrabold text-primary tracking-tight font-headline">硬件设备监控</h1>
        <p class="text-secondary text-sm mt-1">道闸、摄像头及自助终端运行状态</p>
      </div>
    </header>

    <!-- 顶部核心指标摘要卡片 -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8 flex-shrink-0" v-loading="loadingOverview">
       <div class="bg-surface-container-lowest p-4 rounded-xl border border-outline-variant/20 shadow-sm">
          <p class="text-xs font-bold text-secondary uppercase tracking-widest mb-1">总计设备</p>
          <div class="flex items-center justify-between">
             <p class="text-3xl font-black font-headline text-on-surface">{{ overview.total || 0 }}</p>
             <span class="material-symbols-outlined text-secondary opacity-30 text-3xl">developer_board</span>
          </div>
       </div>
       <div class="bg-primary/5 p-4 rounded-xl border border-primary/20 shadow-sm">
          <p class="text-xs font-bold text-primary uppercase tracking-widest mb-1">已连接 在线</p>
          <div class="flex items-center justify-between">
             <p class="text-3xl font-black font-headline text-primary">{{ overview.online || 0 }}</p>
             <span class="material-symbols-outlined text-primary text-3xl">wifi_tethering</span>
          </div>
       </div>
       <div class="bg-error/5 p-4 rounded-xl border border-error/20 shadow-sm shadow-error/10">
          <p class="text-xs font-bold text-error uppercase tracking-widest mb-1">活动故障 严重</p>
          <div class="flex items-center justify-between">
             <p class="text-3xl font-black font-headline text-error">{{ overview.offline || 0 }}</p>
             <span class="material-symbols-outlined text-error text-3xl">error</span>
          </div>
       </div>
       <div class="bg-surface-container-lowest p-4 rounded-xl border border-outline-variant/20 shadow-sm">
          <p class="text-xs font-bold text-amber-600 uppercase tracking-widest mb-1">计划维护</p>
          <div class="flex items-center justify-between">
             <p class="text-3xl font-black font-headline text-amber-600">{{ overview.maintenance || 0 }}</p>
             <span class="material-symbols-outlined text-amber-600 opacity-50 text-3xl">build</span>
          </div>
       </div>
    </div>

    <!-- 筛选 -->
    <div class="flex gap-4 mb-4">
       <el-input v-model="filters.search" placeholder="搜索设备/位置..." size="small" class="w-64" clearable @change="loadDevicesList">
          <template #prefix><span class="material-symbols-outlined text-sm">search</span></template>
       </el-input>
       <el-select v-model="filters.type" placeholder="全部类型" size="small" class="w-32" clearable @change="loadDevicesList">
          <el-option label="全部类型" value="" />
          <el-option label="道闸设备" value="gate" />
          <el-option label="监控摄像头" value="camera" />
          <el-option label="自助终端" value="kiosk" />
          <el-option label="地磁/传感器" value="sensor" />
       </el-select>
       <el-select v-model="filters.status" placeholder="全部状态" size="small" class="w-32" clearable @change="loadDevicesList">
          <el-option label="全部状态" value="" />
          <el-option label="在线" value="online" />
          <el-option label="故障" value="offline" />
          <el-option label="维护中" value="maintenance" />
       </el-select>
    </div>

    <!-- 设备卡片网格 -->
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 flex-1 overflow-auto bg-surface p-2" v-loading="loadingDevices">
      <div v-for="dev in devices" :key="dev.id" class="bg-surface-container-lowest rounded-2xl border transition-all duration-300" :class="dev.status === 'offline' ? 'border-error shadow-sm shadow-error/10' : 'border-outline-variant/20 shadow-sm hover:shadow-md'">
        <div class="p-5">
           <div class="flex justify-between items-start mb-4">
              <div class="flex items-center gap-3">
                 <div class="w-10 h-10 rounded-xl flex items-center justify-center font-bold" :class="dev.status==='offline' ? 'bg-error/10 text-error' : 'bg-primary/10 text-primary'">
                    <span class="material-symbols-outlined">{{ getDevIcon(dev.device_type) }}</span>
                 </div>
                 <div>
                    <h3 class="font-bold text-on-surface">{{ dev.name }}</h3>
                    <p class="text-xs text-secondary">{{ dev.location }}</p>
                 </div>
              </div>
              <!-- 状态标 -->
              <div class="flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-bold border" :class="dev.status === 'offline' ? 'bg-error/10 text-error border-error/20' : (dev.status === 'maintenance' ? 'bg-amber-50 text-amber-600 border-amber-200' : 'bg-green-50 text-green-600 border-green-200')">
                 <span class="w-1.5 h-1.5 rounded-full" :class="dev.status==='offline'?'bg-error animate-pulse':(dev.status==='maintenance'?'bg-amber-500':'bg-green-500')"></span>
                 {{ dev.status_label || (dev.status === 'offline' ? '故障' : (dev.status === 'maintenance' ? '维护中' : '在线')) }}
              </div>
           </div>

           <!-- 详细数据行 -->
           <div class="grid grid-cols-2 gap-4 text-xs text-secondary mt-6" v-if="dev.status === 'online' || dev.status === 'maintenance'">
              <div>
                 <p class="mb-1">设备序列号</p>
                 <p class="font-medium text-on-surface truncate" :title="dev.ip_address || dev.id">{{ dev.ip_address || dev.id }}</p>
              </div>
              <div>
                 <p class="mb-1">近期状态</p>
                 <p class="font-medium text-on-surface">连通正常</p>
              </div>
              <div>
                 <p class="mb-1">最后心跳</p>
                 <p class="font-medium text-on-surface">{{ dev.last_ping ? new Date(dev.last_ping).toLocaleTimeString() : '刚刚' }}</p>
              </div>
              <div>
                 <p class="mb-1">最后更新时间</p>
                 <p class="font-medium text-on-surface">{{ new Date(dev.updated_at).toLocaleDateString() }}</p>
              </div>
           </div>

           <!-- 故障信息 (仅故障状态显示) -->
           <div class="mt-4 p-3 bg-error/5 text-error rounded-xl text-sm" v-else>
              <div class="flex items-start gap-2">
                 <span class="material-symbols-outlined text-sm mt-0.5 relative top-px flex-shrink-0">report</span>
                 <div>
                    <p class="font-bold mb-0.5">问题：{{ dev.errorMsg || '设备连通性丢失或报告硬件故障' }}</p>
                    <p class="text-xs opacity-80">最近一次在线时间：{{ dev.last_ping ? new Date(dev.last_ping).toLocaleString() : '未知' }}</p>
                 </div>
              </div>
           </div>
        </div>

        <!-- 底部操作条 -->
        <div class="border-t border-outline-variant/10 p-3 bg-surface-container-low/50 flex divide-x divide-outline-variant/20">
           <button class="flex-1 text-xs font-bold text-secondary hover:text-primary transition-colors flex items-center justify-center gap-1">
              <span class="material-symbols-outlined text-sm">settings</span> 配置
           </button>
           <button v-if="dev.status==='offline'" class="flex-1 text-xs font-bold text-error hover:opacity-80 transition-opacity flex items-center justify-center gap-1">
              <span class="material-symbols-outlined text-sm">restart_alt</span> 硬件重启
           </button>
           <button v-else class="flex-1 text-xs font-bold text-secondary hover:text-primary transition-colors flex items-center justify-center gap-1">
              <span class="material-symbols-outlined text-sm">restart_alt</span> 软重启
           </button>
        </div>
      </div>
      
      <div v-if="devices.length === 0" class="col-span-full flex items-center justify-center p-12 text-secondary bg-surface-container-lowest border border-dashed rounded-2xl">
         未找到匹配的设备
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 设备网络管理 — 接入真实 API 数据
 */
import { ref, reactive, onMounted } from 'vue'
import { getDevices, getDeviceOverview } from '@/api/device'
import { ElMessage } from 'element-plus'

const loadingOverview = ref(false)
const loadingDevices = ref(false)

const overview = ref({})
const devices = ref([])

const filters = reactive({
   search: '',
   type: '',
   status: ''
})

onMounted(() => {
   loadOverview()
   loadDevicesList()
})

const loadOverview = async () => {
   loadingOverview.value = true
   try {
      const res = await getDeviceOverview()
      overview.value = res
   } catch(e) {
      console.error(e)
   } finally {
      loadingOverview.value = false
   }
}

const loadDevicesList = async () => {
   loadingDevices.value = true
   try {
      const params = {}
      if (filters.search) params.search = filters.search
      if (filters.type) params.device_type = filters.type
      if (filters.status) params.status = filters.status
      
      const res = await getDevices(params)
      devices.value = res.results || res
   } catch(e) {
      ElMessage.error('无法加载设备列表')
   } finally {
      loadingDevices.value = false
   }
}

const getDevIcon = (type) => {
   if (type === 'gate') return 'gate'
   if (type === 'camera') return 'videocam'
   if (type === 'kiosk') return 'point_of_sale'
   return 'sensors'
}
</script>
