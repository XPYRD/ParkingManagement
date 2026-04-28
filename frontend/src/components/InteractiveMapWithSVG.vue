<template>
  <div class="interactive-map-view">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <input 
        v-model="searchPlate"
        type="text" 
        placeholder="输入车牌号寻车，如：京A88888"
        class="search-input"
        @keyup.enter="handleFindCar"
      />
      <button @click="handleFindCar" class="search-btn">🔍 寻车</button>
      <button @click="resetMap" class="reset-btn">↻ 重置</button>
    </div>

    <!-- SVG 底图容器 -->
    <div class="map-wrapper">
      <!-- 直接加载外部 SVG 文件 -->
      <svg 
        ref="svgMap"
        class="svg-map"
        xmlns="http://www.w3.org/2000/svg"
        xmlns:xlink="http://www.w3.org/1999/xlink"
      >
        <!-- SVG 内容将通过 fetch 加载 -->
      </svg>

      <!-- 动态覆盖层：路径规划 + 交互 -->
      <svg class="svg-overlay" ref="overlayMap">
        <defs>
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

        <!-- 起终点标记 -->
        <g id="route-markers">
          <!-- 起点 -->
          <circle 
            v-if="startPoint"
            :cx="startPoint.x"
            :cy="startPoint.y"
            r="12"
            fill="none"
            stroke="#10b981"
            stroke-width="3"
          />
          <text 
            v-if="startPoint"
            :x="startPoint.x"
            :y="startPoint.y - 20"
            text-anchor="middle"
            font-size="12"
            fill="#10b981"
            font-weight="bold"
            background="white"
          >
            START
          </text>

          <!-- 终点 -->
          <circle 
            v-if="endPoint"
            :cx="endPoint.x"
            :cy="endPoint.y"
            r="12"
            fill="none"
            stroke="#f59e0b"
            stroke-width="3"
            stroke-dasharray="5,5"
          />
          <text 
            v-if="endPoint"
            :x="endPoint.x"
            :y="endPoint.y - 20"
            text-anchor="middle"
            font-size="12"
            fill="#f59e0b"
            font-weight="bold"
          >
            TARGET
          </text>
        </g>

        <!-- 路径规划结果 -->
        <polyline 
          v-if="navigationPath && navigationPath.length > 0"
          :points="navigationPath.map(p => `${p.x},${p.y}`).join(' ')"
          fill="none"
          stroke="#3b82f6"
          stroke-width="4"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="route-path"
          opacity="0.8"
        />
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
        </div>
        <div class="detail-actions">
          <button 
            v-if="selectedSpace.status === 0"
            @click="handleNavigateTo(selectedSpace)"
            class="action-btn primary"
          >
            导航到此位置
          </button>
        </div>
      </div>
    </transition>

    <!-- 导航信息面板 -->
    <transition name="slide-right">
      <div v-if="navigationInfo" class="navigation-panel">
        <div class="panel-header">
          <h4>📍 导航信息</h4>
          <button @click="clearNavigation" class="close-btn">✕</button>
        </div>
        <div class="panel-body">
          <div class="info-row">
            <span class="label">总距离:</span>
            <span class="value">{{ navigationInfo.distance?.toFixed(1) || '计算中...' }} px</span>
          </div>
          <div class="info-row">
            <span class="label">路径节点:</span>
            <span class="value">{{ navigationInfo.path?.length || 0 }} 个</span>
          </div>
          <div class="route-steps" v-if="navigationInfo.path && navigationInfo.path.length > 0">
            <div class="steps-title">关键节点坐标:</div>
            <div class="step-items">
              <div 
                v-for="(point, idx) in navigationInfo.path.slice(0, 10)"
                :key="idx"
                class="step-item"
              >
                <span class="step-number">{{ idx + 1 }}</span>
                <span class="step-text">
                  ({{ Math.round(point.x) }}, {{ Math.round(point.y) }})
                </span>
              </div>
              <div v-if="navigationInfo.path.length > 10" class="step-item">
                <span class="step-text">... 共 {{ navigationInfo.path.length }} 个节点</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 错误提示 -->
    <transition name="fade">
      <div v-if="errorMessage" class="error-toast">
        <span>{{ errorMessage }}</span>
        <button @click="errorMessage = ''" class="close-btn">✕</button>
      </div>
    </transition>

    <!-- 加载指示器 -->
    <div v-if="isLoading" class="loading-spinner">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

// ========== 数据状态 ==========
const spaceStatus = ref({})  // 车位状态映射 {space_id: {status, current_plate, ...}}
const selectedSpace = ref(null)
const searchPlate = ref('')
const isLoading = ref(false)
const errorMessage = ref('')

// 导航相关
const navigationPath = ref([])
const navigationInfo = ref(null)
const startPoint = ref(null)
const endPoint = ref(null)

// SVG 引用
const svgMap = ref(null)
const overlayMap = ref(null)

// SVG 尺寸
const svgWidth = ref(1098)
const svgHeight = ref(771)

// ========== 生命周期 ==========
onMounted(async () => {
  await loadSVGMap()
  await loadMapData()
})

// ========== 方法 ==========

/**
 * 从外部文件加载 SVG 底图
 */
async function loadSVGMap() {
  try {
    isLoading.value = true
    const response = await fetch('/backend/svg/interactive_map.svg')
    const svgContent = await response.text()
    
    if (svgMap.value) {
      svgMap.value.innerHTML = svgContent
      
      // 重新设置 viewBox
      const svgElement = svgMap.value.querySelector('svg')
      if (svgElement) {
        svgMap.value.setAttribute('viewBox', '0 0 1098 771')
        svgMap.value.setAttribute('preserveAspectRatio', 'xMidYMid meet')
        
        // 为所有 parking-space 元素添加点击事件
        const spaces = svgMap.value.querySelectorAll('.parking-space')
        spaces.forEach(space => {
          const spaceId = space.getAttribute('id')
          space.addEventListener('click', () => handleSpaceClick(spaceId))
          space.style.cursor = 'pointer'
          space.style.transition = 'fill 0.3s, stroke 0.3s'
        })
      }
    }
  } catch (error) {
    console.error('加载 SVG 地图失败:', error)
    errorMessage.value = '加载地图失败，请刷新重试'
  } finally {
    isLoading.value = false
  }
}

/**
 * 加载地图数据 - 获取所有车位状态
 */
async function loadMapData() {
  try {
    isLoading.value = true
    const response = await axios.get('/api/v1/map/spaces/')
    
    if (response.data.code === 200) {
      // 构建状态映射
      response.data.data.forEach(space => {
        spaceStatus.value[space.space_id] = {
          space_id: space.space_id,
          status: space.status,
          current_plate: space.current_plate || '',
          last_updated: new Date().toISOString()
        }
        
        // 立即更新 SVG 颜色
        updateSpaceColor(space.space_id, space.status)
      })
    }
  } catch (error) {
    console.error('加载地图数据失败:', error)
    errorMessage.value = '加载地图数据失败'
  } finally {
    isLoading.value = false
  }
}

/**
 * 更新 SVG 中车位元素的颜色
 */
function updateSpaceColor(spaceId, status) {
  const spaceElement = svgMap.value?.querySelector(`#${spaceId}`)
  if (!spaceElement) return
  
  let color = '#ffffff'  // 默认白色
  
  if (status === 0) {
    color = '#e0f7fa'  // 浅绿色 - 空闲
  } else if (status === 1) {
    color = '#ffebee'  // 浅红色 - 占用
  } else if (status === 2) {
    color = '#fff3e0'  // 浅黄色 - 维护中
  }
  
  spaceElement.setAttribute('fill', color)
}

/**
 * 获取车位的 SVG 元素中心坐标
 */
function getSpaceCoordinates(spaceId) {
  const spaceElement = svgMap.value?.querySelector(`#${spaceId}`)
  if (!spaceElement) return null
  
  // 获取 transform 属性中的坐标
  const transform = spaceElement.getAttribute('transform')
  if (!transform) return null
  
  // 解析 translate(x, y) 或 matrix 变换
  let x = 0, y = 0
  
  if (transform.includes('translate')) {
    const match = transform.match(/translate\(([\d.-]+)[,\s]+([\d.-]+)\)/)
    if (match) {
      x = parseFloat(match[1]) + 23.3  // 车位宽度 / 2
      y = parseFloat(match[2]) + 39.2  // 车位高度 / 2
    }
  } else if (transform.includes('matrix')) {
    // 处理 matrix 变换 (更复杂的变换)
    const bbox = spaceElement.getBBox()
    x = bbox.x + bbox.width / 2
    y = bbox.y + bbox.height / 2
  }
  
  return { x, y }
}

/**
 * 处理车位点击事件
 */
function handleSpaceClick(spaceId) {
  const space = spaceStatus.value[spaceId]
  if (!space) return
  
  const coords = getSpaceCoordinates(spaceId)
  if (coords) {
    space.center_x = coords.x
    space.center_y = coords.y
  }
  
  selectedSpace.value = space
  
  // 高亮选中的车位
  const spaceElement = svgMap.value?.querySelector(`#${spaceId}`)
  if (spaceElement) {
    spaceElement.setAttribute('stroke', '#3b82f6')
    spaceElement.setAttribute('stroke-width', '3')
  }
}

/**
 * 清除车位高亮
 */
function clearSpaceHighlight() {
  if (selectedSpace.value) {
    const spaceElement = svgMap.value?.querySelector(`#${selectedSpace.value.space_id}`)
    if (spaceElement) {
      spaceElement.setAttribute('stroke', '#7e7e7e')
      spaceElement.setAttribute('stroke-width', '1')
    }
  }
}

/**
 * 寻车功能
 */
async function handleFindCar() {
  clearSpaceHighlight()
  
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
      const space = spaceStatus.value[carData.space_id]
      
      if (space) {
        handleSpaceClick(carData.space_id)
        
        const coords = getSpaceCoordinates(carData.space_id)
        if (coords) {
          endPoint.value = coords
          // 从电梯出发
          startPoint.value = { x: 846, y: 149 }  // 电梯 3 的位置
          calculateRoute()
        }
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
 * 导航到指定车位
 */
function handleNavigateTo(space) {
  const coords = getSpaceCoordinates(space.space_id)
  if (coords) {
    endPoint.value = coords
    startPoint.value = { x: 846, y: 149 }  // 电梯 3 的位置
    calculateRoute()
  }
}

/**
 * 计算路径（前端 Dijkstra 算法）
 */
function calculateRoute() {
  if (!startPoint.value || !endPoint.value) return

  try {
    isLoading.value = true
    
    // 构建导航图
    const graph = buildGraph()
    const path = dijkstra(graph, startPoint.value, endPoint.value)
    
    if (path && path.length > 0) {
      navigationPath.value = path
      
      // 计算总距离
      let totalDistance = 0
      for (let i = 0; i < path.length - 1; i++) {
        const dx = path[i + 1].x - path[i].x
        const dy = path[i + 1].y - path[i].y
        totalDistance += Math.sqrt(dx * dx + dy * dy)
      }
      
      navigationInfo.value = {
        path: path,
        distance: totalDistance
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
 * 构建导航图（所有车位作为节点）
 */
function buildGraph() {
  const nodes = []
  const edges = []
  
  // 添加起点
  nodes.push({ ...startPoint.value, type: 'start' })
  
  // 添加所有车位作为节点
  Object.values(spaceStatus.value).forEach((space, idx) => {
    const coords = getSpaceCoordinates(space.space_id)
    if (coords) {
      nodes.push({ ...coords, spaceId: space.space_id, type: 'space' })
    }
  })
  
  // 添加终点
  nodes.push({ ...endPoint.value, type: 'end' })
  
  // 构建边（连接距离较近的节点）
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const dx = nodes[j].x - nodes[i].x
      const dy = nodes[j].y - nodes[i].y
      const dist = Math.sqrt(dx * dx + dy * dy)
      
      // 连接距离在合理范围内的节点
      if (dist < 400) {
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
  
  // 初始化
  const dist = Array(n).fill(Infinity)
  const prev = Array(n).fill(-1)
  const visited = Array(n).fill(false)
  
  // 找起点和终点
  let startIdx = -1, endIdx = -1
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
  
  // 主循环
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
    
    // 更新相邻节点
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
  clearSpaceHighlight()
  selectedSpace.value = null
  searchPlate.value = ''
  navigationPath.value = []
  navigationInfo.value = null
  startPoint.value = null
  endPoint.value = null
  errorMessage.value = ''
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
  const classes = { 0: 'status-free', 1: 'status-occupied', 2: 'status-maintenance' }
  return classes[space.status] || ''
}
</script>

<style scoped>
.interactive-map-view {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  position: relative;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
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
  position: relative;
}

.svg-map {
  width: 100%;
  height: 100%;
  max-width: 1098px;
  max-height: 771px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

.svg-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 100%;
  max-width: 1098px;
  max-height: 771px;
  pointer-events: none;
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

.step-items {
  max-height: 200px;
  overflow-y: auto;
}

.step-item {
  display: flex;
  gap: 8px;
  margin-bottom: 6px;
  padding: 6px;
  background: #f8fafc;
  border-radius: 4px;
  font-size: 11px;
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  background: #3b82f6;
  color: white;
  border-radius: 50%;
  font-weight: 600;
  font-size: 9px;
  flex-shrink: 0;
}

.step-text {
  color: #475569;
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
</style>
