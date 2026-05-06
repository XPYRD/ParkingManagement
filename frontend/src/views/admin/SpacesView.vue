<template>
  <!-- 车位管理 -->
  <div class="p-6 lg:p-10 h-full flex flex-col">
    <header class="flex justify-between items-end mb-8 flex-shrink-0">
      <div>
        <h1 class="text-3xl font-extrabold text-primary tracking-tight font-headline">车位资产管理</h1>
        <p class="text-secondary text-sm mt-1">全局车位监控与维护调度</p>
      </div>
    </header>

    <!-- 顶部统计 -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8 flex-shrink-0" v-loading="loadingStats">
       <div class="bg-surface-container-lowest p-5 rounded-xl border border-outline-variant/20 shadow-sm flex items-center justify-between">
          <div>
             <p class="text-xs font-bold text-secondary uppercase tracking-widest mb-1">总车位</p>
             <p class="text-2xl font-black font-headline text-on-surface">{{ stats.total }}</p>
          </div>
          <div class="w-10 h-10 rounded-full bg-primary/10 flex flex-shrink-0 items-center justify-center">
             <span class="material-symbols-outlined text-primary">apps</span>
          </div>
       </div>
       <div class="bg-surface-container-lowest p-5 rounded-xl border border-outline-variant/20 shadow-sm flex items-center justify-between">
          <div>
             <p class="text-xs font-bold text-secondary uppercase tracking-widest mb-1">空闲 (目前)</p>
             <p class="text-2xl font-black font-headline text-green-600">{{ stats.free }}</p>
          </div>
          <div class="w-10 h-10 rounded-full bg-green-50 flex flex-shrink-0 items-center justify-center">
             <span class="material-symbols-outlined text-green-600">check_circle</span>
          </div>
       </div>
       <div class="bg-surface-container-lowest p-5 rounded-xl border border-outline-variant/20 shadow-sm flex items-center justify-between">
          <div>
             <p class="text-xs font-bold text-secondary uppercase tracking-widest mb-1">已占用/预约</p>
             <p class="text-2xl font-black font-headline text-primary">{{ stats.occupied + stats.reserved }}</p>
          </div>
          <div class="w-10 h-10 rounded-full bg-primary/10 flex flex-shrink-0 items-center justify-center">
             <span class="material-symbols-outlined text-primary">directions_car</span>
          </div>
       </div>
       <div class="bg-surface-container-lowest p-5 rounded-xl border border-outline-variant/20 shadow-sm flex items-center justify-between border-error/30 bg-error/5">
          <div>
             <p class="text-xs font-bold text-error uppercase tracking-widest mb-1">维护中</p>
             <p class="text-2xl font-black font-headline text-error">{{ stats.maintenance }}</p>
          </div>
          <div class="w-10 h-10 rounded-full bg-error/10 flex flex-shrink-0 items-center justify-center">
             <span class="material-symbols-outlined text-error">build</span>
          </div>
       </div>
    </div>

    <!-- 筛选与表格 -->
    <div class="flex-1 bg-surface-container-lowest rounded-2xl border border-outline-variant/20 shadow-sm flex flex-col overflow-hidden">
      <!-- 工具栏 -->
      <div class="p-4 border-b border-outline-variant/20 flex flex-wrap gap-4 items-center justify-between bg-surface-container-low/50">
         <div class="flex gap-4 items-center">
            <el-input v-model="filters.search" placeholder="搜索车位编号或车牌..." size="small" class="w-[440px]" clearable @change="handleSearch">
               <template #prefix><span class="material-symbols-outlined text-sm">search</span></template>
            </el-input>
            <el-select v-model="filters.floor" placeholder="楼层" size="small" class="w-48" clearable @change="handleSearch">
               <el-option label="B2层" value="B2" />
               <el-option label="B1层" value="B1" />
               <el-option label="1层" value="1F" />
            </el-select>
            <el-select v-model="filters.type" placeholder="车位类型" size="small" class="w-48" clearable @change="handleSearch">
               <el-option label="标准车位" value="standard" />
               <el-option label="充电桩" value="ev" />
            </el-select>
            <el-select v-model="filters.status" placeholder="状态" size="small" class="w-48" clearable @change="handleSearch">
               <el-option label="空闲" value="free" />
               <el-option label="占用" value="occupied" />
               <el-option label="预约" value="reserved" />
               <el-option label="维护" value="maintenance" />
            </el-select>
         </div>
      </div>
      
      <!-- 表格部分 -->
      <div class="flex-1 overflow-auto p-4" v-loading="loadingTable">
        <el-table :data="tableData" style="width: 100%" stripe>
          <el-table-column prop="spot_id" label="车位编号" width="120">
             <template #default="{ row }">
                <span class="font-bold font-headline text-on-surface">{{ row.spot_id }}</span>
             </template>
          </el-table-column>
          <el-table-column label="楼层/区域" width="150">
             <template #default="{ row }">
                 {{ row.floor }}层 {{ row.zone }}区
             </template>
          </el-table-column>
          <el-table-column label="类型" width="150">
             <template #default="{ row }">
                <div class="flex items-center gap-1.5">
                   <span class="material-symbols-outlined text-sm" :class="row.spot_type==='ev'?'text-blue-500':(row.spot_type==='vip'?'text-amber-500':'text-secondary')">
                      {{ row.spot_type==='ev'?'ev_station':(row.spot_type==='vip'?'star':'local_parking') }}
                   </span>
                   <span class="text-sm">{{ row.spot_type_label }}</span>
                </div>
             </template>
          </el-table-column>
          <el-table-column prop="status" label="当前状态">
            <template #default="{ row }">
               <el-tag 
                  size="small" 
                  effect="plain" 
                  class="!font-bold !rounded-full"
                  :type="row.status === 'free' ? 'success' : (row.status === 'maintenance' ? 'danger' : (row.status === 'reserved' ? 'warning' : 'primary'))"
               >
                 {{ row.status_label }}
               </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
               <el-button link type="warning" size="small" v-if="row.status !== 'maintenance'" @click="handlePauseSpot(row)">修停</el-button>
               <el-button link type="success" size="small" v-else @click="handleResumeSpot(row)">恢复</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <div class="p-4 border-t border-outline-variant/20 flex justify-end">
         <el-pagination 
            v-model:current-page="currentPage" 
            :page-size="pageSize" 
            background layout="total, prev, pager, next" 
            :total="totalSpots" 
            @current-change="handlePageChange"
         />
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 车位管理后台 — 接入 API 真实数据
 */
import { ref, reactive, onMounted } from 'vue'
import { getSpots } from '@/api/parking'
import { getDashboardOverview } from '@/api/dashboard'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const filters = reactive({
  search: '',
  floor: '',
  type: '',
  status: ''
})

const stats = reactive({
  total: 0,
  free: 0,
  occupied: 0,
  reserved: 0,
  maintenance: 0
})

const tableData = ref([])
const loadingStats = ref(false)
const loadingTable = ref(false)

const currentPage = ref(1)
const pageSize = ref(10) // 假设后端默认分页大小 10
const totalSpots = ref(0)

onMounted(() => {
  loadStats()
  loadSpotsList()
})

const loadStats = async () => {
    loadingStats.value = true
    try {
        const dashboard = await getDashboardOverview()
        Object.assign(stats, dashboard.occupancy)
    } catch(err) {
        console.error('加载车位统计失败', err)
    } finally {
        loadingStats.value = false
    }
}

const loadSpotsList = async () => {
    loadingTable.value = true
    try {
        const params = {
           page: currentPage.value,
           ...(filters.search && filters.search.trim() && { search: filters.search.trim() }),
           ...(filters.floor && filters.floor.trim() && { floor: filters.floor.trim() }),
           ...(filters.type && filters.type.trim() && { type: filters.type.trim() }),
           ...(filters.status && filters.status.trim() && { status: filters.status.trim() })
        }
        const res = await getSpots(params)
        if (res.results) {
            tableData.value = res.results
            totalSpots.value = res.count
        } else {
            tableData.value = res
            totalSpots.value = res.length
        }
    } catch(err) {
        ElMessage.error('获取车位列表失败')
    } finally {
        loadingTable.value = false
    }
}

const handleSearch = () => {
    currentPage.value = 1
    loadSpotsList()
}

const handlePageChange = (page) => {
    currentPage.value = page
    loadSpotsList()
}

const handlePauseSpot = async (row) => {
    try {
        // 调用 API 修停车位
        await updateSpotStatus(row.id, true)
        row.status = 'maintenance'
        row.status_label = '维护中'
        ElMessage.success('车位已修停')
    } catch (err) {
        ElMessage.error('修停失败')
    }
}

const handleResumeSpot = async (row) => {
    try {
        // 调用 API 恢复车位
        await updateSpotStatus(row.id, false)
        row.status = 'free'
        row.status_label = '空闲'
        ElMessage.success('车位已恢复')
    } catch (err) {
        ElMessage.error('恢复失败')
    }
}

const updateSpotStatus = async (spotId, isMaintenance) => {
    // 使用 toggle-maintenance 接口切换维修状态
    const res = await request.post(`/parking/spots/${spotId}/toggle-maintenance/`, { maintenance: isMaintenance })
    return res
}
</script>
