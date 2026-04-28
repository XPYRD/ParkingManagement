<template>
  <div class="interactive-map-container">
    <!-- 地图搜索栏 -->
    <div class="search-bar">
      <select
        v-model="selectedStartSpotId"
        class="location-select"
        @change="handleStartPointChange"
      >
        <option value="">请选择我当前位置</option>
        <option
          v-for="start in startPointOptions"
          :key="start.id"
          :value="String(start.id)"
        >
          {{ start.label }} ({{ start.floor }})
        </option>
      </select>

      <input 
        v-model="searchQuery"
        type="text" 
        placeholder="搜索车位号，如：A001"
        class="search-input"
        @keyup.enter="handleSearchSpace"
      />
      <button @click="handleSearchSpace" class="search-btn">搜索</button>

      <div class="divider"></div>

      <input 
        v-model="findCarPlate"
        type="text" 
        placeholder="输入车牌号反向寻车"
        class="search-input find-car-input"
        @keyup.enter="handleFindCarByPlate"
      />
      <button @click="handleFindCarByPlate" class="search-btn find-car-btn">反向寻车</button>
      <button @click="resetMap" class="reset-btn">重置</button>
    </div>

    <!-- SVG 地图容器 -->
    <div class="map-wrapper">
      <svg 
        ref="svgMap"
        :viewBox="`0 0 ${mapWidth} ${mapHeight}`"
        class="svg-map"
        xmlns="http://www.w3.org/2000/svg"
      >
        <!-- 背景网格 -->
        <defs>
          <pattern id="gridPattern" width="50" height="50" patternUnits="userSpaceOnUse">
            <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#e0e7ff" stroke-width="0.5"/>
          </pattern>
          
          <!-- 路径流动动画 -->
          <style>
            .route-path {
              stroke-dasharray: 8, 4;
              animation: flowAnimation 1s linear infinite;
            }
            @keyframes flowAnimation {
              0% { stroke-dashoffset: 0; }
              100% { stroke-dashoffset: 12; }
            }
          </style>
        </defs>

        <!-- 底图背景 -->
        <rect width="100%" height="100%" fill="url(#gridPattern)" />
        
        <!-- 背景建筑轮廓 -->
        <g id="background-layer" opacity="0.3">
          <rect x="20" y="20" width="960" height="760" fill="none" stroke="#1e293b" stroke-width="2"/>
          <!-- 柱子和墙体 -->
          <rect x="450" y="150" width="100" height="700" fill="#cbd5e1" opacity="0.5"/>
          <rect x="150" y="350" width="700" height="100" fill="#cbd5e1" opacity="0.3"/>
        </g>

        <!-- 路径规划结果层 (绘制在车位之下) -->
        <g id="route-layer">
          <!-- 动态绘制的导航路径会在这里 -->
          <polyline 
            v-if="navigationPath && navigationPath.length > 0"
            :points="navigationPath.map(p => `${p.x},${p.y}`).join(' ')"
            fill="none"
            stroke="#3b82f6"
            stroke-width="3"
            class="route-path"
            opacity="0.8"
          />
        </g>

        <!-- 车位层 (业务数据层) -->
        <g id="parking-spaces-layer">
          <g 
            v-for="space in spaceStatus"
            :key="space.space_id"
            :class="['parking-space', getSpaceClass(space)]"
            @click="handleSpaceClick(space)"
          >
            <!-- 车位矩形背景 -->
            <rect 
              :x="space.center_x - 20"
              :y="space.center_y - 30"
              width="40"
              height="60"
              rx="4"
              :fill="getSpaceColor(space)"
              :stroke="space.space_id === selectedSpaceId ? '#3b82f6' : 'transparent'"
              stroke-width="2"
              class="space-rect"
            />
            
            <!-- 车位编号文字 -->
            <text
              :x="space.center_x"
              :y="space.center_y + 5"
              text-anchor="middle"
              font-size="12"
              font-weight="bold"
              fill="#1e293b"
              pointer-events="none"
            >
              {{ extractSpaceNumber(space.space_id) }}
            </text>

            <!-- 已占用时显示车牌号 -->
            <text
              v-if="space.status === 'occupied' && space.current_plate"
              :x="space.center_x"
              :y="space.center_y - 20"
              text-anchor="middle"
              font-size="9"
              fill="#dc2626"
              pointer-events="none"
            >
              {{ space.current_plate }}
            </text>
          </g>
        </g>

        <!-- 起终点标记 -->
        <g id="route-markers">
          <!-- 起点（电梯/出口） -->
          <circle 
            v-if="startPoint"
            :cx="startPoint.x"
            :cy="startPoint.y"
            r="8"
            fill="none"
            stroke="#10b981"
            stroke-width="2"
          />
          <text 
            v-if="startPoint"
            :x="startPoint.x"
            :y="startPoint.y - 12"
            text-anchor="middle"
            font-size="10"
            fill="#10b981"
            font-weight="bold"
          >
            起点
          </text>

          <!-- 终点（目标车位） -->
          <circle 
            v-if="endPoint"
            :cx="endPoint.x"
            :cy="endPoint.y"
            r="8"
            fill="none"
            stroke="#f59e0b"
            stroke-width="2"
          />
          <text 
            v-if="endPoint"
            :x="endPoint.x"
            :y="endPoint.y - 12"
            text-anchor="middle"
            font-size="10"
            fill="#f59e0b"
            font-weight="bold"
          >
            目标
          </text>
        </g>
      </svg>
    </div>

    <!-- 车位详情卡片 -->
    <transition name="slide-up">
      <div v-if="selectedSpace" class="detail-card">
        <div class="detail-header">
          <h3>{{ selectedSpace.space_id }}</h3>
          <button @click="selectedSpace = null" class="close-btn">✕</button>
        </div>
        <div class="detail-body">
          <div class="detail-row">
            <span class="label">状态:</span>
            <span :class="['value', getStatusClass(selectedSpace)]">
              {{ getStatusLabel(selectedSpace) }}
            </span>
          </div>
          <div v-if="selectedSpace.current_plate" class="detail-row">
            <span class="label">车牌:</span>
            <span class="value">{{ selectedSpace.current_plate }}</span>
          </div>
          <div class="detail-row">
            <span class="label">坐标:</span>
            <span class="value">({{ Math.round(selectedSpace.center_x) }}, {{ Math.round(selectedSpace.center_y) }})</span>
          </div>
          <div class="detail-row">
            <span class="label">更新时间:</span>
            <span class="value">{{ formatTime(selectedSpace.last_updated) }}</span>
          </div>
        </div>
        <div class="detail-actions">
          <button 
            v-if="selectedSpace.status === 'free'"
            @click="handleNavigateTo(selectedSpace)"
            class="action-btn primary"
          >
            导航到此位置
          </button>
          <button 
            v-if="selectedSpace.status === 'occupied'"
            @click="handleFindCarFromPlate(selectedSpace.current_plate)"
            class="action-btn secondary"
          >
            查看该车信息
          </button>
        </div>
      </div>
    </transition>

    <!-- 导航信息面板 -->
    <transition name="slide-right">
      <div v-if="navigationInfo" class="navigation-panel">
        <div class="panel-header">
          <h4>导航信息</h4>
          <button @click="clearNavigation" class="close-btn">✕</button>
        </div>
        <div class="panel-body">
          <div class="info-row">
            <span class="label">总距离:</span>
            <span class="value">{{ navigationInfo.distance?.toFixed(2) || '计算中...' }} m</span>
          </div>
          <div class="info-row">
            <span class="label">路径节点:</span>
            <span class="value">{{ navigationInfo.path?.length || 0 }} 个</span>
          </div>
          <div class="route-steps" v-if="navigationInfo.steps && navigationInfo.steps.length > 0">
            <div class="steps-title">导航步骤:</div>
            <div 
              v-for="(step, idx) in navigationInfo.steps"
              :key="idx"
              class="step-item"
            >
              <span class="step-number">{{ idx + 1 }}</span>
              <span class="step-text">
                从 <strong>{{ step.from }}</strong> 前往 <strong>{{ step.to }}</strong>
                ({{ step.distance?.toFixed(2) || '?' }}m)
              </span>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 加载指示器 -->
    <div v-if="isLoading" class="loading-spinner">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 错误提示 -->
    <transition name="fade">
      <div v-if="errorMessage" class="error-toast">
        <span>{{ errorMessage }}</span>
        <button @click="errorMessage = ''" class="close-btn">✕</button>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import axios from 'axios'

const spaceStatus = ref([])
const startPointOptions = ref([])
const selectedStartSpotId = ref('')
const selectedSpace = ref(null)
const selectedSpaceId = ref(null)
const searchQuery = ref('')
const findCarPlate = ref('')
const isLoading = ref(false)
const errorMessage = ref('')

const mapWidth = ref(1000)
const mapHeight = ref(800)

const navigationPath = ref([])
const navigationInfo = ref(null)
const startPoint = ref(null)
const endPoint = ref(null)
const svgMap = ref(null)

const spotBySpaceId = computed(() => {
  const map = new Map()
  for (const spot of spaceStatus.value) {
    map.set(spot.space_id, spot)
  }
  return map
})

const startPointById = computed(() => {
  const map = new Map()
  for (const start of startPointOptions.value) {
    map.set(String(start.id), start)
  }
  return map
})

onMounted(async () => {
  await Promise.all([loadMapData(), loadStartPoints()])
  if (startPointOptions.value.length > 0) {
    selectedStartSpotId.value = String(startPointOptions.value[0].id)
    handleStartPointChange()
  }
})

async function loadMapData() {
  try {
    isLoading.value = true
    const response = await axios.get('/api/v1/map/spaces/')
    if (response.data.code !== 200) {
      throw new Error('地图数据返回异常')
    }

    spaceStatus.value = response.data.data.map((space) => {
      const cx = Number.isFinite(space.center_x) ? space.center_x : space.x
      const cy = Number.isFinite(space.center_y) ? space.center_y : space.y
      return {
        id: space.id,
        space_id: space.space_id,
        floor: space.floor,
        node_type: space.node_type,
        location_name: space.location_name || '',
        status: space.status,
        current_plate: space.current_plate || '',
        center_x: Number.isFinite(cx) ? cx : null,
        center_y: Number.isFinite(cy) ? cy : null,
        last_updated: space.last_updated,
      }
    }).filter((spot) => Number.isFinite(spot.center_x) && Number.isFinite(spot.center_y))
  } catch (error) {
    console.error('加载地图数据失败:', error)
    errorMessage.value = '加载地图数据失败，请刷新重试'
  } finally {
    isLoading.value = false
  }
}

async function loadStartPoints() {
  try {
    const response = await axios.get('/api/v1/map/start-points/')
    if (response.data.code !== 200) {
      throw new Error('导航起点返回异常')
    }
    startPointOptions.value = response.data.data.filter(
      (item) => Number.isFinite(item.center_x) && Number.isFinite(item.center_y)
    )
  } catch (error) {
    console.error('加载导航起点失败:', error)
    errorMessage.value = '加载导航起点失败，请检查后台起点配置'
  }
}

function handleStartPointChange() {
  const selected = startPointById.value.get(String(selectedStartSpotId.value))
  if (!selected) {
    startPoint.value = null
    return
  }
  startPoint.value = { x: selected.center_x, y: selected.center_y }
}

function handleSpaceClick(space) {
  selectedSpace.value = space
  selectedSpaceId.value = space.space_id
}

async function handleSearchSpace() {
  const query = searchQuery.value.trim()
  if (!query) {
    errorMessage.value = '请输入车位号'
    return
  }

  try {
    isLoading.value = true
    const spaceId = query.toLowerCase().startsWith('space_') ? query : `space_${query.toUpperCase()}`
    const response = await axios.get('/api/v1/map/find_car/', { params: { space_id: spaceId } })

    if (response.data.code === 200) {
      const data = response.data.data
      const targetSpot = spotBySpaceId.value.get(data.space_id)
      if (targetSpot) {
        selectedSpace.value = targetSpot
        selectedSpaceId.value = targetSpot.space_id
        // 搜索车位时仅定位，不强制导航，除非用户手动点击导航按钮
      } else {
        errorMessage.value = `地图中未找到车位 ${data.space_id}`
      }
    }
  } catch (error) {
    errorMessage.value = '搜索车位失败'
  } finally {
    isLoading.value = false
  }
}

async function handleFindCarByPlate() {
  if (!selectedStartSpotId.value) {
    errorMessage.value = '请先选择“我现在在”位置'
    return
  }

  const plate = findCarPlate.value.trim()
  if (!plate) {
    errorMessage.value = '请输入车牌号'
    return
  }

  try {
    isLoading.value = true
    const response = await axios.get('/api/v1/map/find_car/', { params: { plate_number: plate } })

    if (response.data.code === 200) {
      const carData = response.data.data
      const targetSpot = spotBySpaceId.value.get(carData.space_id)
      if (targetSpot) {
        selectedSpace.value = targetSpot
        selectedSpaceId.value = targetSpot.space_id
        await calculateRouteBySpotIds(Number(selectedStartSpotId.value), Number(carData.spot_id || targetSpot.id))
      }
    }
  } catch (error) {
    if (error.response?.status === 404) {
      errorMessage.value = '未找到该车牌号的车辆'
    } else {
      errorMessage.value = '反向寻车失败'
    }
  } finally {
    isLoading.value = false
  }
}

async function handleFindCar() {

async function handleFindCarFromPlate(plate) {
  findCarPlate.value = plate || ''
  await handleFindCarByPlate()
}

async function handleNavigateTo(space) {
  if (!selectedStartSpotId.value) {
    errorMessage.value = '请先选择“我现在在”位置'
    return
  }
  await calculateRouteBySpotIds(Number(selectedStartSpotId.value), Number(space.id))
}

function buildPolylineFromSteps(steps) {
  const points = []
  for (const step of steps || []) {
    if (Array.isArray(step.from_coords) && step.from_coords.length >= 2) {
      const [x, y] = step.from_coords
      if (points.length === 0 || points[points.length - 1].x !== x || points[points.length - 1].y !== y) {
        points.push({ x, y })
      }
    }
    if (Array.isArray(step.to_coords) && step.to_coords.length >= 2) {
      const [x, y] = step.to_coords
      points.push({ x, y })
    }
  }
  return points
}

async function calculateRouteBySpotIds(startSpotId, endSpotId) {
  try {
    isLoading.value = true
    const response = await axios.post('/api/v1/parking/navigation/find-path/', {
      start_spot_id: startSpotId,
      end_spot_id: endSpotId,
    })

    const result = response.data
    navigationInfo.value = result
    navigationPath.value = buildPolylineFromSteps(result.steps)

    if (navigationPath.value.length > 0) {
      startPoint.value = navigationPath.value[0]
      endPoint.value = navigationPath.value[navigationPath.value.length - 1]
    }
  } catch (error) {
    console.error('路径计算错误:', error)
    if (error.response?.data?.error) {
      errorMessage.value = error.response.data.error
    } else {
      errorMessage.value = '路径计算失败'
    }
  } finally {
    isLoading.value = false
  }
}

function resetMap() {
  selectedSpace.value = null
  selectedSpaceId.value = null
  searchQuery.value = ''
  findCarPlate.value = ''
  navigationPath.value = []
  navigationInfo.value = null
  endPoint.value = null
  if (selectedStartSpotId.value) {
    handleStartPointChange()
  }
}

function clearNavigation() {
  navigationPath.value = []
  navigationInfo.value = null
  endPoint.value = null
  if (selectedStartSpotId.value) {
    handleStartPointChange()
  }
}

function getSpaceColor(space) {
  if (space.status === 'free') return '#e0f7fa'
  if (space.status === 'occupied') return '#ffebee'
  if (space.status === 'reserved') return '#fff7e6'
  if (space.status === 'maintenance') return '#fff3e0'
  return '#f5f5f5'
}

function getSpaceClass(space) {
  return {
    'space-free': space.status === 'free',
    'space-occupied': space.status === 'occupied',
    'space-reserved': space.status === 'reserved',
    'space-maintenance': space.status === 'maintenance',
    'space-selected': space.space_id === selectedSpaceId.value,
  }
}

function getStatusLabel(space) {
  const labels = {
    free: '空闲',
    occupied: '占用',
    reserved: '已预约',
    maintenance: '维护中',
  }
  return labels[space.status] || '未知'
}

function getStatusClass(space) {
  const classes = {
    free: 'status-free',
    occupied: 'status-occupied',
    reserved: 'status-reserved',
    maintenance: 'status-maintenance',
  }
  return classes[space.status] || ''
}

function extractSpaceNumber(spaceId) {
  return (spaceId || '').replace('space_', '')
}

function formatTime(timeStr) {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  if (Number.isNaN(date.getTime())) return '-'
  return date.toLocaleTimeString('zh-CN')
}
</script>

<style scoped>
.interactive-map-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  position: relative;
  overflow: hidden;
}

/* 搜索栏 */
.search-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  z-index: 10;
}

.search-input {
  flex: 1;
  max-width: 250px;
  padding: 10px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
}

.divider {
  width: 1px;
  height: 24px;
  background: #e2e8f0;
  margin: 0 8px;
}

.find-car-btn {
  background: #10b981 !important;
}

.find-car-btn:hover {
  background: #059669 !important;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
}

.location-select {
  min-width: 220px;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  color: #334155;
  background: #fff;
}

.location-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-btn,
.reset-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.search-btn {
  background: #3b82f6;
  color: white;
}

.search-btn:hover {
  background: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.reset-btn {
  background: #f1f5f9;
  color: #64748b;
}

.reset-btn:hover {
  background: #e2e8f0;
}

/* 地图容器 */
.map-wrapper {
  flex: 1;
  overflow: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.svg-map {
  width: 100%;
  height: 100%;
  max-width: 1000px;
  max-height: 800px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

/* 车位样式 */
.parking-space {
  cursor: pointer;
}

.parking-space:hover .space-rect {
  filter: brightness(0.95);
  stroke: #3b82f6 !important;
  stroke-width: 2;
}

.space-rect {
  transition: all 0.2s;
}

.space-free .space-rect {
  fill: #e0f7fa;
}

.space-occupied .space-rect {
  fill: #ffebee;
}

.space-maintenance .space-rect {
  fill: #fff3e0;
}

.space-reserved .space-rect {
  fill: #fff7e6;
}

.space-selected .space-rect {
  stroke: #3b82f6;
  stroke-width: 2;
  filter: brightness(0.9);
}

/* 详情卡片 */
.detail-card {
  position: absolute;
  bottom: 20px;
  left: 20px;
  width: 300px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  z-index: 20;
  animation: slideUp 0.3s ease-out;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.detail-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.detail-body {
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
}

.detail-row:last-child {
  margin-bottom: 0;
}

.label {
  color: #64748b;
  font-weight: 500;
}

.value {
  color: #1e293b;
  font-weight: 600;
}

.value.status-free {
  color: #10b981;
}

.value.status-occupied {
  color: #ef4444;
}

.value.status-maintenance {
  color: #f59e0b;
}

.value.status-reserved {
  color: #ea580c;
}

.detail-actions {
  padding: 12px 16px;
  display: flex;
  gap: 8px;
}

.action-btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn.primary {
  background: #3b82f6;
  color: white;
}

.action-btn.primary:hover {
  background: #2563eb;
}

.action-btn.secondary {
  background: #f1f5f9;
  color: #3b82f6;
}

.action-btn.secondary:hover {
  background: #e2e8f0;
}

/* 导航面板 */
.navigation-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 300px;
  max-height: 600px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  z-index: 20;
  display: flex;
  flex-direction: column;
  animation: slideRight 0.3s ease-out;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.panel-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
}

.route-steps {
  margin-top: 16px;
  border-top: 1px solid #f1f5f9;
  padding-top: 12px;
}

.steps-title {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 8px;
}

.step-item {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  padding: 8px;
  background: #f8fafc;
  border-radius: 6px;
  font-size: 12px;
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  background: #3b82f6;
  color: white;
  border-radius: 50%;
  font-weight: 600;
  font-size: 10px;
  flex-shrink: 0;
}

.step-text {
  color: #475569;
}

/* 加载指示器 */
.loading-spinner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  z-index: 50;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(59, 130, 246, 0.2);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-spinner p {
  color: #64748b;
  font-size: 14px;
}

/* 错误提示 */
.error-toast {
  position: absolute;
  bottom: 20px;
  right: 20px;
  padding: 12px 16px;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 50;
  animation: slideUp 0.3s ease-out;
}

/* 动画 */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.slide-up-enter-active,
.slide-up-leave-active,
.slide-right-enter-active,
.slide-right-leave-active,
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

.slide-right-enter-from,
.slide-right-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .interactive-map-container {
    height: auto;
  }

  .search-bar {
    flex-direction: column;
  }

  .search-input {
    max-width: 100%;
  }

  .detail-card,
  .navigation-panel {
    position: fixed;
    width: calc(100% - 40px);
    max-width: 100%;
  }

  .detail-card {
    bottom: 20px;
    left: 20px;
    right: 20px;
  }

  .navigation-panel {
    top: auto;
    bottom: 360px;
    left: 20px;
    right: 20px;
  }
}
</style>
