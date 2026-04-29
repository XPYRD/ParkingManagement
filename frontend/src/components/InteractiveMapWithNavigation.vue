<template>
  <div class="interactive-map-container">
    <!-- 地图搜索栏 -->
    <div class="search-bar">
      <input
        v-model="searchPlate"
        type="text"
        placeholder="输入车牌号寻车，如：京A88888"
        class="search-input"
        @keyup.enter="handleFindCar"
      />
      <button @click="handleFindCar" class="search-btn">寻车</button>
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
              v-if="space.status === 1 && space.current_plate"
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
            v-if="selectedSpace.status === 0"
            @click="handleNavigateTo(selectedSpace)"
            class="action-btn primary"
          >
            导航到此位置
          </button>
          <button
            v-if="selectedSpace.status === 1"
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
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'

// ========== 数据状态 ==========
const spaceStatus = ref([])  // 车位状态数据
const selectedSpace = ref(null)  // 选中的车位
const selectedSpaceId = ref(null)
const searchPlate = ref('')  // 搜索的车牌号
const isLoading = ref(false)
const errorMessage = ref('')

// 地图尺寸
const mapWidth = ref(1000)
const mapHeight = ref(800)

// 导航相关
const navigationPath = ref([])  // 前端绘制的路径坐标数组
const navigationInfo = ref(null)  // 后端返回的导航信息
const startPoint = ref(null)  // 起点坐标
const endPoint = ref(null)  // 终点坐标
const svgMap = ref(null)

// ========== 初始化 ==========
onMounted(async () => {
  await loadMapData()
  initializeTestData()  // 测试数据初始化
})

// ========== 方法 ==========

/**
 * 加载地图数据 - 获取所有车位状态
 */
async function loadMapData() {
  try {
    isLoading.value = true
    const response = await axios.get('/api/v1/map/spaces/')

    if (response.data.code === 200) {
      // 转换后端数据为前端格式
      spaceStatus.value = response.data.data.map(space => ({
        space_id: space.space_id,
        status: space.status,
        current_plate: space.current_plate || '',
        center_x: Math.random() * 900 + 50,  // 实际应该从后端获取坐标
        center_y: Math.random() * 700 + 50,
        last_updated: new Date().toISOString()
      }))
    }
  } catch (error) {
    console.error('加载地图数据失败:', error)
    errorMessage.value = '加载地图数据失败，请刷新重试'
  } finally {
    isLoading.value = false
  }
}

/**
 * 初始化测试数据（开发阶段）
 */
function initializeTestData() {
  // 生成测试的停车空间
  if (spaceStatus.value.length === 0) {
    const testSpaces = []
    const rows = 4
    const cols = 6
    const spacingX = 140
    const spacingY = 160

    for (let i = 0; i < rows; i++) {
      for (let j = 0; j < cols; j++) {
        const isOccupied = Math.random() > 0.6
        testSpaces.push({
          space_id: `space_${String.fromCharCode(65 + i)}${String(j + 1).padStart(2, '0')}`,
          status: isOccupied ? 1 : 0,
          current_plate: isOccupied ? `京A${Math.floor(Math.random() * 100000)}` : '',
          center_x: 80 + j * spacingX,
          center_y: 100 + i * spacingY,
          last_updated: new Date().toISOString()
        })
      }
    }
    spaceStatus.value = testSpaces
  }
}

/**
 * 处理车位点击事件
 */
function handleSpaceClick(space) {
  selectedSpace.value = space
  selectedSpaceId.value = space.space_id
}

/**
 * 寻车功能
 */
async function handleFindCar() {
  if (!searchPlate.value.trim()) {
    errorMessage.value = '请输入车牌号'
    return
  }

  try {
    isLoading.value = true
    const response = await axios.get('/api/v1/map/find_car/', {
      params: { plate_number: searchPlate.value }
    })

    if (response.data.code === 200) {
      const carData = response.data.data
      const space = spaceStatus.value.find(s => s.space_id === carData.space_id)

      if (space) {
        selectedSpace.value = space
        selectedSpaceId.value = space.space_id
        // 设置终点为找到的车位
        endPoint.value = { x: space.center_x, y: space.center_y }
        // 从电梯出口导航到该车位
        await calculateRoute()
      }
    }
  } catch (error) {
    if (error.response?.status === 404) {
      errorMessage.value = error.response.data.error || '未找到该车牌号'
    } else {
      errorMessage.value = '寻车失败，请稍后重试'
    }
  } finally {
    isLoading.value = false
  }
}

/**
 * 根据车牌号处理寻车
 */
async function handleFindCarFromPlate(plate) {
  searchPlate.value = plate
  await handleFindCar()
}

/**
 * 导航到指定车位
 */
async function handleNavigateTo(space) {
  endPoint.value = { x: space.center_x, y: space.center_y }
  // 模拟从电梯出口开始
  startPoint.value = { x: 900, y: 50 }
  await calculateRoute()
}

/**
 * 计算路径（前端 Dijkstra 算法）
 */
async function calculateRoute() {
  if (!startPoint.value || !endPoint.value) return

  try {
    isLoading.value = true

    // 构建简化的图
    const graph = buildGraph()
    const path = dijkstra(graph, startPoint.value, endPoint.value)

    if (path && path.length > 0) {
      navigationPath.value = path

      // 计算距离和步骤
      let totalDistance = 0
      const steps = []

      for (let i = 0; i < path.length - 1; i++) {
        const from = path[i]
        const to = path[i + 1]
        const distance = Math.sqrt(
          Math.pow(to.x - from.x, 2) + Math.pow(to.y - from.y, 2)
        )
        totalDistance += distance

        // 查找对应的空间信息用于步骤描述
        const fromSpace = spaceStatus.value.find(s =>
          Math.abs(s.center_x - from.x) < 5 && Math.abs(s.center_y - from.y) < 5
        )
        const toSpace = spaceStatus.value.find(s =>
          Math.abs(s.center_x - to.x) < 5 && Math.abs(s.center_y - to.y) < 5
        )

        steps.push({
          from: fromSpace?.space_id || `坐标(${Math.round(from.x)},${Math.round(from.y)})`,
          to: toSpace?.space_id || `坐标(${Math.round(to.x)},${Math.round(to.y)})`,
          distance: distance
        })
      }

      navigationInfo.value = {
        path: path,
        distance: totalDistance,
        steps: steps
      }
    } else {
      errorMessage.value = '无法计算路径，目标不可达'
    }
  } catch (error) {
    console.error('路径计算错误:', error)
    errorMessage.value = '路径计算失败'
  } finally {
    isLoading.value = false
  }
}

/**
 * 构建导航图
 */
function buildGraph() {
  const nodes = []
  const edges = []

  // 添加起点
  nodes.push(startPoint.value)

  // 添加所有空闲车位作为可达节点
  spaceStatus.value.forEach(space => {
    nodes.push({ x: space.center_x, y: space.center_y, spaceId: space.space_id })
  })

  // 添加终点
  nodes.push(endPoint.value)

  // 构建边（节点间的连接）
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const dist = Math.sqrt(
        Math.pow(nodes[j].x - nodes[i].x, 2) +
        Math.pow(nodes[j].y - nodes[i].y, 2)
      )
      // 只连接距离较近的节点
      if (dist < 300) {
        edges.push({ from: i, to: j, weight: dist })
        edges.push({ from: j, to: i, weight: dist })
      }
    }
  }

  return { nodes, edges }
}

/**
 * Dijkstra 最短路径算法
 */
function dijkstra(graph, start, end) {
  const { nodes, edges } = graph
  const n = nodes.length

  // 初始化距离和前驱节点
  const dist = Array(n).fill(Infinity)
  const prev = Array(n).fill(-1)
  const visited = Array(n).fill(false)

  // 查找起点和终点的索引
  let startIdx = -1
  let endIdx = -1

  for (let i = 0; i < nodes.length; i++) {
    if (Math.abs(nodes[i].x - start.x) < 5 && Math.abs(nodes[i].y - start.y) < 5) {
      startIdx = i
    }
    if (Math.abs(nodes[i].x - end.x) < 5 && Math.abs(nodes[i].y - end.y) < 5) {
      endIdx = i
    }
  }

  if (startIdx === -1 || endIdx === -1) return null

  dist[startIdx] = 0

  // 执行 Dijkstra 算法
  for (let count = 0; count < n; count++) {
    let minDist = Infinity
    let u = -1

    for (let i = 0; i < n; i++) {
      if (!visited[i] && dist[i] < minDist) {
        minDist = dist[i]
        u = i
      }
    }

    if (u === -1) break

    visited[u] = true

    // 更新相邻节点的距离
    for (const edge of edges) {
      if (edge.from === u && !visited[edge.to]) {
        if (dist[u] + edge.weight < dist[edge.to]) {
          dist[edge.to] = dist[u] + edge.weight
          prev[edge.to] = u
        }
      }
    }
  }

  // 重建路径
  const path = []
  let current = endIdx

  while (current !== -1) {
    path.unshift({ x: nodes[current].x, y: nodes[current].y })
    current = prev[current]
  }

  return path.length > 1 ? path : null
}

/**
 * 重置地图
 */
function resetMap() {
  selectedSpace.value = null
  selectedSpaceId.value = null
  searchPlate.value = ''
  navigationPath.value = []
  navigationInfo.value = null
  startPoint.value = null
  endPoint.value = null
}

/**
 * 清除导航
 */
function clearNavigation() {
  navigationPath.value = []
  navigationInfo.value = null
  startPoint.value = null
  endPoint.value = null
}

/**
 * 获取车位颜色
 */
function getSpaceColor(space) {
  if (space.status === 0) return '#e0f7fa'  // 浅绿色 - 空闲
  if (space.status === 1) return '#ffebee'  // 浅红色 - 占用
  if (space.status === 2) return '#fff3e0'  // 浅黄色 - 维护中
  return '#f5f5f5'  // 默认灰色
}

/**
 * 获取车位样式类
 */
function getSpaceClass(space) {
  return {
    'space-free': space.status === 0,
    'space-occupied': space.status === 1,
    'space-maintenance': space.status === 2,
    'space-selected': space.space_id === selectedSpaceId.value
  }
}

/**
 * 获取状态标签
 */
function getStatusLabel(space) {
  const labels = { 0: '空闲', 1: '占用', 2: '维护中' }
  return labels[space.status] || '未知'
}

/**
 * 获取状态样式类
 */
function getStatusClass(space) {
  const classes = {
    0: 'status-free',
    1: 'status-occupied',
    2: 'status-maintenance'
  }
  return classes[space.status] || ''
}

/**
 * 提取车位号
 */
function extractSpaceNumber(spaceId) {
  return spaceId.replace('space_', '')
}

/**
 * 格式化时间
 */
function formatTime(timeStr) {
  const date = new Date(timeStr)
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
  max-width: 400px;
  padding: 10px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
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
