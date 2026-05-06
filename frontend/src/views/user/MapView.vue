/**
 * 🚗 智能地图集成示例 - MapView 完整页面
 * 
 * 包含:
 * ✅ 地图渲染与交互
 * ✅ 数据加载与轮询
 * ✅ 搜索、过滤、排序
 * ✅ 智能推荐逻辑
 * ✅ 实时占用率统计
 * ✅ 响应式布局
 */

<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
    <!-- 页面头部 -->
    <header class="bg-white shadow-sm sticky top-0 z-20">
      <div class="px-4 md:px-8 max-w-7xl mx-auto py-6 space-y-4">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 class="text-3xl font-extrabold text-slate-900">智能地图</h1>
            <p class="text-slate-600 text-sm mt-1">蓝色空闲车位 · 绿色充电桩车位 · 黄色已预约车位 · 红色已占用车位 · 灰色维修中车位</p>
          </div>
          
          <!-- 楼层切换 -->
          <div class="flex gap-3 mt-4 md:mt-0">
            <button 
              v-for="floor in floors"
              :key="floor"
              @click="currentFloor = floor"
              :class="[
                'px-4 py-2 rounded-lg font-semibold transition-all',
                currentFloor === floor 
                  ? 'bg-blue-600 text-white shadow-lg' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
            >
              {{ floor }}
            </button>
          </div>
        </div>
        
        <!-- 统一搜索与过滤 -->
        <div class="flex flex-col md:flex-row gap-3">
          <!-- 起点选择 -->
          <div class="w-full md:w-80 relative">
             <select 
              v-model="selectedStartId"
              class="w-full px-4 py-2 border border-blue-200 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white"
            >
              <option :value="null">-- 选择我的位置 (如电梯或起始车位) --</option>
              <optgroup label="公共地标">
                <option v-for="node in startNodes" :key="'landmark-'+node.id" :value="node.id">
                  {{ node.name }}
                </option>
              </optgroup>
              <optgroup label="所有车位">
                <option v-for="spot in allSpots.filter(s => s.spot_id)" :key="'spot-'+spot.id" :value="spot.id">
                  🅿️ {{ spot.spot_id }}
                </option>
              </optgroup>
            </select>
          </div>

          <!-- 统一搜索框 -->
          <div class="flex-1 relative">
            <span class="absolute left-3 top-3 text-gray-400">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
            </span>
            <input 
              v-model="searchQuery"
              type="text"
              placeholder="输入车牌号或车位号 (如：京A88888 或 A001)"
              @keyup.enter="handleUnifiedSearch"
              class="w-full pl-10 pr-4 py-2 border border-blue-100 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white shadow-sm"
            />
          </div>

          <div class="flex gap-2">
            <button 
              @click="handleUnifiedSearch"
              :disabled="isLoading"
              class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all font-medium flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
              搜索
            </button>

            <button 
              @click="handlePlateSearch"
              :disabled="isSearchingPlate || !searchQuery"
              class="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:bg-gray-400 transition-all font-bold shadow-md shadow-emerald-100 flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
              <span v-if="!isSearchingPlate">反向寻车</span>
              <span v-else>寻车中...</span>
            </button>
          </div>
          
          <!-- 状态过滤 -->
          <select 
            v-model="statusFilter"
            class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">所有状态</option>
            <option value="free">空闲</option>
            <option value="occupied">已占用</option>
            <option value="reserved">已预约</option>
            <option value="maintenance">维修中</option>
          </select>
          
          <!-- 刷新按钮 -->
          <button 
            @click="loadSpots"
            :disabled="isLoading"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-all"
          >
            <span v-if="!isLoading">🔄 刷新</span>
            <span v-else>加载中...</span>
          </button>
        </div>

        <div v-if="carSearchResult" class="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
          <div class="flex justify-between items-center">
            <div>
              车牌 {{ carSearchResult.plate_number }} 位于 {{ carSearchResult.space_id.replace(/^space_/, '') }}，楼层 {{ carSearchResult.floor || '未知' }}。
              <span v-if="carSearchResult.location_desc && carSearchResult.location_desc !== 'Unknown'">提示：{{ carSearchResult.location_desc }}</span>
            </div>
            <div v-if="navigationInfo" class="flex gap-4 font-bold text-emerald-700">
              <span>距离: {{ navigationInfo.distance }}m</span>
              <span>耗时: {{ navigationInfo.duration }}s</span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 主要内容区 -->
    <main class="px-4 md:px-8 max-w-7xl mx-auto py-8">
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <!-- 左侧: 地图区 (3/4 宽度) -->
        <div class="lg:col-span-3 space-y-4">
          <!-- 图例 -->
          <div class="flex flex-wrap gap-6 p-4 bg-white rounded-lg shadow-sm">
            <div v-for="legend in legends" :key="legend.status" class="flex items-center gap-2">
              <div :class="['w-4 h-4 rounded-sm', legend.colorClass]"></div>
              <span class="text-sm text-gray-700 font-medium">{{ legend.label }}</span>
            </div>
          </div>
          
          <!-- 地图容器（单一Canvas：SVG背景 + 标记 + 缩放/平移） -->
          <div class="relative bg-white rounded-2xl shadow-lg overflow-hidden">
            <!-- 加载状态 -->
            <div v-if="isLoading" class="absolute inset-0 bg-white/50 flex items-center justify-center z-50">
              <div class="text-center">
                <div class="inline-block animate-spin rounded-full h-12 w-12 border border-blue-200 border-t-blue-600"></div>
                <p class="mt-2 text-gray-700 font-semibold">加载地图数据...</p>
              </div>
            </div>
            
            <!-- Canvas 地图（SVG背景 + 停车位标记 + 内部缩放/平移） -->
            <div class="aspect-[1098/771] w-full">
              <ParkingMapSVGv3 
                :spots="filteredSpots"
                :selectedId="selectedSpot?.id"
                :navigationPath="navigationPath"
                @select="handleSpotClick"
              />
            </div>
          </div>
          
          <!-- AI 推荐卡片 -->
          <transition name="slide-up">
            <div v-if="recommendedSpot && !selectedSpot" class="bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200 rounded-xl p-4 flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">✨</div>
                <div>
                  <p class="text-xs font-bold text-blue-600 uppercase tracking-widest">AI 智能推荐</p>
                  <p class="text-sm text-slate-700 mt-1">
                    车位 <span class="font-black text-blue-600">{{ recommendedSpot.spot_id }}</span> 
                    离入口最近
                  </p>
                </div>
              </div>
              <button 
                @click="handleSpotClick(recommendedSpot)"
                class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
              >
                查看
              </button>
            </div>
          </transition>
        </div>
        
        <!-- 右侧: 侧边栏 (1/4 宽度) -->
        <aside class="space-y-4">
          <!-- 楼层统计卡片 -->
          <div class="bg-white rounded-xl shadow-sm p-6 space-y-4">
            <h3 class="font-bold text-slate-900 text-lg">楼层统计</h3>
            
            <!-- 占用率环形图 -->
            <div class="flex justify-center py-4">
              <div class="relative w-32 h-32">
                <svg viewBox="0 0 100 100" class="transform -rotate-90">
                  <!-- 背景圆 -->
                  <circle cx="50" cy="50" r="40" fill="none" stroke="#e5e7eb" stroke-width="8"/>
                  <!-- 进度圆 -->
                  <circle 
                    cx="50" cy="50" r="40" fill="none" 
                    stroke="#3b82f6" stroke-width="8"
                    stroke-linecap="round"
                    :stroke-dasharray="`${floorOccupancy * 2.51} 251`"
                    class="transition-all duration-700"
                  />
                </svg>
                <div class="absolute inset-0 flex flex-col items-center justify-center">
                  <span class="text-3xl font-extrabold text-blue-600">{{ floorOccupancy }}%</span>
                  <span class="text-xs text-gray-600 mt-1">已占用</span>
                </div>
              </div>
            </div>
            
            <!-- 统计数据 -->
            <div class="grid grid-cols-2 gap-3 pt-2">
              <div class="text-center p-3 bg-blue-50 rounded-lg">
                <p class="text-2xl font-bold text-blue-600">{{ freeCount }}</p>
                <p class="text-xs text-gray-600 mt-1">空闲</p>
              </div>
              <div class="text-center p-3 bg-red-50 rounded-lg">
                <p class="text-2xl font-bold text-red-600">{{ occupiedCount }}</p>
                <p class="text-xs text-gray-600 mt-1">已占用</p>
              </div>
            </div>
          </div>
          
          <!-- 容量提示 -->
          <div 
            :class="[
              'rounded-xl p-4 text-white font-semibold',
              capacityStatus.color === 'green' ? 'bg-green-500' :
              capacityStatus.color === 'yellow' ? 'bg-yellow-500' :
              capacityStatus.color === 'orange' ? 'bg-orange-500' :
              'bg-red-500'
            ]"
          >
            <p class="text-sm">{{ capacityStatus.label }}</p>
            <p class="text-2xl font-bold mt-2">{{ capacityStatus.message }}</p>
          </div>
          
          <!-- 已选择车位详情 -->
          <transition name="slide-in">
            <div v-if="selectedSpot" class="bg-white rounded-xl shadow-sm p-6 space-y-3">
              <h3 class="font-bold text-slate-900 text-lg">{{ selectedSpot.spot_id }}</h3>
              
              <!-- 状态标签 -->
              <div>
                <p class="text-xs text-gray-600 font-semibold uppercase">状态</p>
                <p :class="[
                  'text-sm font-bold mt-1',
                  selectedSpot.status === 'free' ? 'text-green-600' :
                  selectedSpot.status === 'occupied' ? 'text-red-600' :
                  selectedSpot.status === 'reserved' ? 'text-yellow-600' :
                  'text-gray-600'
                ]">
                  {{ statusMap[selectedSpot.status] }}
                </p>
              </div>
              
              <!-- 车位类型 -->
              <div>
                <p class="text-xs text-gray-600 font-semibold uppercase">类型</p>
                <p class="text-sm font-bold mt-1 text-slate-900">{{ typeMap[selectedSpot.spot_type] }}</p>
              </div>
              
              <!-- 区域位置 -->
              <div>
                <p class="text-xs text-gray-600 font-semibold uppercase">位置</p>
                <p class="text-sm font-bold mt-1 text-slate-900">
                  {{ selectedSpot.zone }}区 - {{ selectedSpot.floor }}
                </p>
              </div>
              
              <!-- 车牌号信息 -->
              <div>
                <p class="text-xs text-gray-600 font-semibold uppercase">车牌号</p>
                <p class="text-sm font-bold mt-1 text-slate-900">
                  {{ selectedSpot.current_plate || selectedSpot.reserved_plate || '无' }}
                </p>
              </div>
              
              <!-- 预约按钮 -->
              <button 
                v-if="selectedSpot.status === 'free'"
                @click="goToReserve(selectedSpot)"
                class="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold transition-all"
              >
                立即预约
              </button>
              
              <!-- 不可预约提示 -->
              <button 
                v-else
                disabled
                class="w-full px-4 py-3 bg-gray-300 text-gray-600 rounded-lg cursor-not-allowed font-semibold"
              >
                该车位不可预约
              </button>
            </div>
          </transition>
        </aside>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ParkingMapSVGv3 from '@/components/ParkingMapSVGv3.vue'
import { getSpacesByFloor, findCarByPlate } from '@/api/parking'
import { calculateNavigationPath, getNavigationStartPoints } from '@/api/map'
import { usePlateStore } from '@/stores/plate'

const router = useRouter()
const plateStore = usePlateStore()

// ═════════════════ 状态管理 ═════════════════

const floors = ['B2', 'B1', '1F']  // ✅ 正确的楼层顺序
const currentFloor = ref('B2')  // ✅ 默认显示 B2

const searchQuery = ref('')
const statusFilter = ref('')
const isSearchingPlate = ref(false)
const carSearchResult = ref(null)

const allSpots = ref([])
const selectedSpot = ref(null)
const isLoading = ref(false)
const searchedSpotId = ref(null)  // 记录搜索到的车位ID

const navigationPath = ref([]) // 路径点坐标列表
const navigationInfo = ref(null) // 导航距离时间信息
const startNodes = ref([]) // 可作为起点的地标 (电梯、楼梯等)
const selectedStartId = ref(null) // 用户选择的起点 ID

// 状态映射
const statusMap = {
  'free': '空闲',
  'occupied': '已占用',
  'reserved': '已预约',
  'maintenance': '维修中',
  'overstay': '超时占用'
}

const typeMap = {
  'standard': '标准车位',
  'compact': '紧凑车位',
  'ev': '充电桩',
  'vip': 'VIP 车位',
  'accessible': '无障碍车位'
}

const legends = [
  { status: 'free', label: '空闲', colorClass: 'bg-blue-500' },
  { status: 'occupied', label: '已占用', colorClass: 'bg-red-500' },
  { status: 'reserved', label: '已预约', colorClass: 'bg-yellow-500' },
  { status: 'ev', label: '充电桩', colorClass: 'bg-green-500' },
  { status: 'maintenance', label: '维修中', colorClass: 'bg-gray-300' }
]

// ═════════════════ 计算属性 ═════════════════

/**
 * 过滤后的车位列表（仅显示车位，排除地标）
 */
const filteredSpots = computed(() => {
  return allSpots.value.filter(spot => {
    // 基础过滤：必须是车位类型
    if (spot.node_type === 'location') return false
    
    // 如果有搜索结果，只显示该车位
    if (searchedSpotId.value && spot.space_id !== searchedSpotId.value) {
      return false
    }
    
    // 状态过滤
    const matchStatus = !statusFilter.value || spot.status === statusFilter.value
    
    return matchStatus
  })
})

/**
 * 楼层占用率 (百分比)
 */
const floorOccupancy = computed(() => {
  if (allSpots.value.length === 0) return 0
  
  const occupied = allSpots.value.filter(spot =>
    ['occupied', 'overstay'].includes(spot.status)
  ).length
  
  return Math.round((occupied / allSpots.value.length) * 100)
})

/**
 * 空闲车位数
 */
const freeCount = computed(() => {
  return allSpots.value.filter(s => s.status === 'free').length
})

/**
 * 已占用车位数
 */
const occupiedCount = computed(() => {
  return allSpots.value.filter(s =>
    ['occupied', 'overstay'].includes(s.status)
  ).length
})

/**
 * 容量状态提示
 */
const capacityStatus = computed(() => {
  const rate = floorOccupancy.value
  
  if (rate <= 20) {
    return { label: '宽松', color: 'green', message: '车位充足，可放心停泊' }
  }
  if (rate <= 50) {
    return { label: '适中', color: 'yellow', message: '车位尚可，建议快速停下' }
  }
  if (rate <= 80) {
    return { label: '紧张', color: 'orange', message: '车位紧张，请尽快停下' }
  }
  return { label: '已满', color: 'red', message: '暂无可用车位' }
})

/**
 * AI 推荐车位 (离入口最近的空闲位)
 */
const recommendedSpot = computed(() => {
  const freeSpots = allSpots.value.filter(s => s.status === 'free')
  
  if (freeSpots.length === 0) return null
  
  // 按距离入口排序
  return freeSpots.sort((a, b) => {
    const distA = Math.abs(a.floor_x - 10) + Math.abs(a.floor_y - 50)
    const distB = Math.abs(b.floor_x - 10) + Math.abs(b.floor_y - 50)
    return distA - distB
  })[0]
})

// ═════════════════ 方法 ═════════════════

/**
 * 加载车位数据
 */
async function loadSpots() {
  isLoading.value = true
  try {
    const res = await getSpacesByFloor(currentFloor.value)
    
    const spotsData = res.data || res || []
    
    // 筛选出所有“地标”或“电梯”等非停车位的点作为起点建议
    // 后端对应的字段是 location_name 和 node_type === 'location'
    startNodes.value = spotsData
      .filter(s => s.node_type === 'location' || (s.location_name && s.location_name.trim()))
      .map(s => ({
        id: s.id,
        name: s.location_name || s.space_id,
        space_id: s.space_id
      }))

    if (!selectedStartId.value && startNodes.value.length > 0) {
      selectedStartId.value = startNodes.value[0].id
    }
    
    console.log('Detected start nodes:', startNodes.value)
    
    // 数据转换（确保必要字段存在）
    allSpots.value = spotsData.map(s => {
      const displaySpaceId = (s.space_id || '').replace(/^space_/, '')
      
      // 提取停车位编号用于 zone 判断
      const spaceNum = parseInt(s.space_id?.match(/\d+/)?.[0] || 0)
      
      return {
        id: s.id ?? s.space_id,
        spot_id: s.node_type === 'location' ? null : displaySpaceId,
        space_id: s.space_id,
        location_name: s.location_name,
        node_type: s.node_type,
        spot_type: s.type ? 'ev' : (s.spot_type || 'standard'),
        status: s.is_damaged
          ? 'maintenance'
          : (String(s.reserved_plate || '').trim()
            ? 'reserved'
            : (s.current_plate ? 'occupied' : 'free')),
        is_damaged: Boolean(s.is_damaged),
        marker_color: s.marker_color || null,
        floor: s.floor,
        rotation: s.rotation || 0,
        // Canvas 使用原始 SVG 坐标
        zone: (spaceNum >= 37 && spaceNum <= 47) ? 'B' : 'A',
        // SVG 原始坐标（直接用于 Canvas 绘制）
        floor_x: s.x || 0,
        floor_y: s.y || 0,
        // 备用字段
        x: s.x,
        y: s.y,
        center_x: s.center_x,
        center_y: s.center_y,
        current_plate: s.current_plate,
        reserved_plate: s.reserved_plate
      }
    })
    
    ElMessage.success('地图已更新')
  } catch (err) {
    console.error('加载失败:', err)
    ElMessage.error('无法加载地图数据')
  } finally {
    isLoading.value = false
  }
}

/**
 * 统一搜索处理（支持车位号或车牌号）
 * 仅做查找和高亮，不自动触发寻车
 */
async function handleUnifiedSearch() {
  const query = searchQuery.value.trim()
  if (!query) {
    ElMessage.warning('请输入搜索内容')
    return
  }

  // 1. 尝试作为车位号查找 (如 A001 -> space_A001)
  const isSpaceFormat = /^[A-Z]\d{3}$/i.test(query) || query.toLowerCase().startsWith('space_')
  if (isSpaceFormat) {
    const formattedId = query.toLowerCase().startsWith('space_') ? query : `space_${query.toUpperCase()}`
    const matched = allSpots.value.find(s => s.space_id === formattedId)
    if (matched) {
      selectedSpot.value = matched
      searchedSpotId.value = null
      if (selectedStartId.value) {
        await triggerNavigation(matched.id)
      }
      ElMessage.success(`已找到车位 ${query}`)
      return
    }
  }

  // 2. 如果不是车位号或当前楼层未找到车位，尝试作为车牌号调用后端接口查找
  try {
    isLoading.value = true
    const res = await findCarByPlate(query)
    const data = res?.data || {}
    
    // 如果找到了车辆
    if (data.space_id) {
      carSearchResult.value = data
      
      // 检查是否需要切换楼层
      if (data.floor && data.floor !== currentFloor.value) {
        currentFloor.value = data.floor
        await loadSpots()
      }
      
      const matched = allSpots.value.find(s => s.space_id === data.space_id)
      if (matched) {
        selectedSpot.value = matched
        ElMessage.success(`车辆位于 ${data.space_id.replace('space_', '')}`)
        if (selectedStartId.value) {
          await triggerNavigation(matched.id)
        }
        return
      }
    }
  } catch (err) {
    // 忽略错误，继续提示未找到
  }
  
  ElMessage.info('当前楼层未找到匹配的车位或车辆')
}

/**
 * 反向寻车处理
 * 支持车牌号或车位号作为目标，提供详细信息显示
 */
async function handlePlateSearch() {
  const query = searchQuery.value.trim()
  if (!query) {
    ElMessage.warning('请输入车牌号或车位号以寻车')
    return
  }

  isSearchingPlate.value = true
  carSearchResult.value = null
  searchedSpotId.value = null

  try {
    // 逻辑：如果是车位号格式，直接尝试定位；否则按车牌查
    const isSpaceFormat = /^[A-Z]\d{3}$/i.test(query) || query.toLowerCase().startsWith('space_')
    
    if (isSpaceFormat) {
      const spaceId = query.toLowerCase().startsWith('space_') ? query : `space_${query.toUpperCase()}`
      const matched = allSpots.value.find(s => s.space_id === spaceId)
      
      carSearchResult.value = { 
        space_id: spaceId, 
        floor: currentFloor.value,
        location_desc: matched ? '位于当前楼层' : '需在其他楼层查找'
      }
      
      if (matched) {
        selectedSpot.value = matched
        ElMessage.success(`已在地图中定位到车位 ${query}`)
      } else {
        ElMessage.info(`车位 ${query} 可能在其他楼层`)
      }
    } else {
      // 按车牌查
      const res = await findCarByPlate(query)
      const data = res?.data || {}
      carSearchResult.value = data
      searchedSpotId.value = data.space_id

      if (data.floor && data.floor !== currentFloor.value) {
        currentFloor.value = data.floor
        await loadSpots()
      }

      const matched = allSpots.value.find(s => s.space_id === data.space_id)
      if (matched) {
        selectedSpot.value = matched
      }
      
      // 触发路径规划
      const finalTargetId = data.id || matched?.id
      if (finalTargetId) {
        await triggerNavigation(finalTargetId)
      } else {
        console.warn('Could not find numeric ID for target:', data.space_id)
      }
      
      ElMessage.success(`已找到车辆：${data.space_id.replace(/^space_/, '')}`)
    }
  } catch (err) {
    const errorMsg = err?.response?.data?.error || '未找到匹配的车辆信息'
    ElMessage.error(errorMsg)
  } finally {
    isSearchingPlate.value = false
  }
}

/**
 * 触发导航路径计算
 */
async function triggerNavigation(targetSpotId) {
  console.log('--- Navigation Started ---')
  console.log('Target ID:', targetSpotId)
  console.log('Start ID:', selectedStartId.value)

  if (!selectedStartId.value) {
    ElMessage.info('请选择“我的位置”以显示寻车路径')
    navigationPath.value = []
    return
  }
  
  if (!targetSpotId) {
    console.warn('No target spot ID provided')
    return
  }

  const startSpot = allSpots.value.find(s => Number(s.id) === Number(selectedStartId.value))
  if (!startSpot) {
    selectedStartId.value = null
    navigationPath.value = []
    ElMessage.warning('当前起点不在本楼层，请重新选择“我的位置”')
    return
  }

  try {
    const res = await calculateNavigationPath(selectedStartId.value, targetSpotId)
    console.log('API Response:', res)
    const pathPoints = Array.isArray(res?.path_points) && res.path_points.length > 0
      ? res.path_points
      : Array.isArray(res?.steps)
        ? res.steps.flatMap((step, index) => {
            const points = []
            if (index === 0 && step?.from_coords) {
              points.push(step.from_coords)
            }
            if (step?.to_coords) {
              points.push(step.to_coords)
            }
            return points
          })
        : []

    if (pathPoints.length > 0) {
      navigationPath.value = pathPoints
      console.log('Set navigationPath with', pathPoints.length, 'points')
      navigationInfo.value = {
        distance: res.distance,
        duration: res.duration
      }
    } else {
      console.warn('API returned no path')
      navigationPath.value = []
    }
  } catch (err) {
    console.error('路径计算失败:', err)
    const backendMessage = err?.response?.data?.error || err?.response?.data?.detail || '无法规划寻车路线'
    ElMessage.error(backendMessage)
    navigationPath.value = []
  }
}

/**
 * 点击车位处理
 */
function handleSpotClick(spot) {
  selectedSpot.value = spot
  if (selectedStartId.value) {
    triggerNavigation(spot.id)
  }
}

/**
 * 跳转到预约页面
 */
function goToReserve(spot) {
  const spotPk = Number(spot?.id)
  router.push({
    name: 'Reserve',
    query: {
      reservationMode: 'specific',
      spotId: Number.isFinite(spotPk) && spotPk > 0 ? String(spotPk) : '',
      spaceId: spot?.space_id || '',
      floor: spot?.floor || '',
      spotType: spot?.spot_type || ''
    }
  })
}

// ═════════════════ 生命周期 ═════════════════

onMounted(() => {
  if (plateStore.plateNumber && !searchQuery.value) {
    searchQuery.value = plateStore.plateNumber
  }
  // 初始加载停车位数据
  loadSpots()
})

watch(searchQuery, (val) => {
  plateStore.setPlateNumber(val)
})

watch(
  () => plateStore.plateNumber,
  (val) => {
    if (val !== searchQuery.value) {
      searchQuery.value = val
    }
  },
)

// 楼层切换时重新加载（同时清除搜索过滤）
watch(currentFloor, () => {
  selectedSpot.value = null
  searchedSpotId.value = null
  carSearchResult.value = null
  navigationPath.value = [] // 切换楼层时重置路径表
  navigationInfo.value = null
  loadSpots()
})

// 监听起点切换，如果已有目标则重新计算路径
watch(selectedStartId, (newStart) => {
  if (newStart && selectedSpot.value) {
    triggerNavigation(selectedSpot.value.id)
  } else if (!newStart) {
    navigationPath.value = []
    navigationInfo.value = null
  }
})
</script>

<style scoped>
/* 下滑进入动画 */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* 右滑进入动画 */
.slide-in-enter-active,
.slide-in-leave-active {
  transition: all 0.3s ease;
}

.slide-in-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.slide-in-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
