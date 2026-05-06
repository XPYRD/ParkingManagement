<template>
  <!-- 反向寻车 — 从 stitch_/_3/code.html 转换 -->
  <div class="px-4 md:px-8 max-w-7xl mx-auto py-8">
    <header class="mb-8 text-center max-w-2xl mx-auto">
      <h1 class="text-3xl font-extrabold text-primary tracking-tight font-headline">反向寻车</h1>
      <p class="text-secondary text-sm mt-2">忘记爱车停在哪了？输入车牌号，一键开启室内导航。</p>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
      <!-- 左侧：搜索面板 -->
      <div class="md:col-span-5 lg:col-span-4 space-y-6">
        <!-- 搜索框 -->
        <div class="glass-panel p-6 rounded-2xl shadow-lg border border-white/40 bg-surface-container-lowest">
          <h2 class="text-lg font-bold text-on-surface mb-4">寻找车辆</h2>
          <el-form>
            <el-form-item>
              <el-input
                v-model="plateNumber"
                placeholder="请输入完整车牌号 (例: 京A88888)"
                size="large"
                class="!text-lg font-bold"
                clearable
              >
                <template #prefix>
                  <span class="material-symbols-outlined text-secondary">directions_car</span>
                </template>
              </el-input>
            </el-form-item>
            <el-button
              type="primary"
              size="large"
              class="!w-full !rounded-xl !py-5 !font-bold"
              :loading="searching"
              @click="handleSearch"
            >
              寻 找
            </el-button>
          </el-form>

          <!-- 快速选择自己的车 -->
          <div class="mt-6 pt-6 border-t border-outline-variant/20">
            <p class="text-xs font-bold text-secondary uppercase tracking-widest mb-3">我的车辆</p>
            <div class="flex gap-2 flex-wrap">
              <el-tag
                v-for="car in myCars"
                :key="car"
                class="cursor-pointer hover:!bg-primary hover:!text-white transition-colors"
                @click="quickSelect(car)"
              >
                {{ car }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 结果卡片 -->
        <transition name="el-zoom-in-top">
          <div v-if="searchResult" class="bg-primary text-white rounded-2xl p-6 shadow-xl relative overflow-hidden">
            <div class="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full blur-2xl -mt-10 -mr-10"></div>
            
            <div class="relative z-10">
              <div class="flex items-center gap-2 mb-1">
                <span class="material-symbols-outlined text-white/80 text-sm">check_circle</span>
                <span class="text-xs font-bold text-white/80 uppercase tracking-widest">已找到车辆</span>
              </div>
              <p class="text-2xl font-black font-headline tracking-widest mb-4">{{ searchResult.plate }}</p>
              
              <div class="space-y-2 mb-6">
                <div class="flex justify-between items-center bg-white/10 p-3 rounded-lg">
                  <span class="text-sm font-medium">停放位置</span>
                  <span class="text-lg font-bold">{{ searchResult.location }}</span>
                </div>
                <div class="flex justify-between items-center px-2">
                  <span class="text-xs text-white/70">入场时间</span>
                  <span class="text-xs font-semibold">{{ searchResult.entryTime }}</span>
                </div>
                <div class="flex justify-between items-center px-2">
                  <span class="text-xs text-white/70">已停放时长</span>
                  <span class="text-xs font-semibold">{{ searchResult.duration }}</span>
                </div>
              </div>

            </div>
          </div>
        </transition>
      </div>

      <!-- 右侧：地图展示 -->
      <div class="md:col-span-7 lg:col-span-8 bg-surface-container-low rounded-2xl min-h-[500px] border border-outline-variant/20 flex flex-col items-center justify-center relative overflow-hidden">
        <!-- 占位地图 -->
        <div v-if="!searchResult" class="text-center p-8">
          <div class="w-20 h-20 bg-surface-container-high rounded-full flex items-center justify-center mx-auto mb-4 text-secondary/30">
            <span class="material-symbols-outlined text-4xl">map</span>
          </div>
          <p class="text-secondary font-medium">在左侧输入车牌号以查看停放位置</p>
        </div>

        <div v-else class="absolute inset-0 bg-cover bg-center" style="background-image: url('https://lh3.googleusercontent.com/aida-public/AB6AXuAaKx8GH8Kh1j9kDqWPxaPoMcBpS5gEnwgqxqnZoqDHPGsqiKX8s19YQXKHgIbS_mYpxiepibFCQEPmprfG9AjKcjBMXMeFCrdipNXBKHQqZr0xK6nH2jEdMvGK6iOu9cLMTIp_J3fQMOqcU3aJxlAWQp4SUm65i1RdT-qqPaCBOJT2p8Ly_BU3iRlTIYPLlpHUPVxHtXaBGbQRQRQWMRj8GJjHqW1s9KJ8kWrBopXN5bK-9Yoj9oLMOo7xSJ_lKhwIJvO0fETBJFqj'); opacity: 0.3;">
        </div>
        
        <div v-if="searchResult" class="relative z-10 flex flex-col items-center">
            <!-- 模拟导航路线动画 -->
            <div class="w-64 h-64 border-2 border-primary border-dashed rounded-full flex items-center justify-center animate-[spin_10s_linear_infinite]">
                 <span class="material-symbols-outlined text-4xl text-primary transform -rotate-45">near_me</span>
            </div>
            <div class="mt-4 bg-surface p-4 rounded-xl shadow-lg flex items-center gap-4 text-on-surface">
                <span class="material-symbols-outlined text-green-500">directions_walk</span>
                <div>
                    <p class="font-bold">距离车辆 120 米</p>
                    <p class="text-xs text-secondary">预计步行约 2 分钟</p>
                </div>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 反向寻车 — 接入真实 API 数据
 */
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getVehicles } from '@/api/user'
import { getSessions } from '@/api/parking'

const plateNumber = ref('')
const searching = ref(false)
const searchResult = ref(null)

const myCars = ref([])

onMounted(async () => {
  try {
    const vehicles = await getVehicles()
    myCars.value = vehicles.map(v => v.plate_number)
  } catch (e) {
    console.error('Failed to load vehicles', e)
  }
})

function quickSelect(plate) {
  plateNumber.value = plate
  handleSearch()
}

async function handleSearch() {
  if (!plateNumber.value) {
    ElMessage.warning('请输入车牌号')
    return
  }

  searching.value = true
  searchResult.value = null

  try {
    const res = await getSessions({ search: plateNumber.value })
    const sessions = res.results || res
    const activeSession = sessions.find(s => !s.exit_time)
    
    if (activeSession && activeSession.spot_detail) {
      const spot = activeSession.spot_detail
      const entryDate = new Date(activeSession.entry_time)
      const now = new Date()
      const diffHrs = Math.floor((now - entryDate) / 3600000)
      const diffMins = Math.floor(((now - entryDate) % 3600000) / 60000)
      
      searchResult.value = {
        plate: plateNumber.value,
        location: `${spot.floor}层 - ${spot.zone}区 - ${spot.spot_id}`,
        entryTime: entryDate.toLocaleString(),
        duration: `${diffHrs}小时 ${diffMins}分钟`
      }
    } else {
      ElMessage.info('未找到该车辆的在场记录')
    }
  } catch (err) {
    ElMessage.error('查询失败，请稍后重试')
  } finally {
    searching.value = false
  }
}

</script>
