<template>
  <div class="multi-floor-container">
    <!-- 楼层选择器 -->
    <div class="floor-selector">
      <div class="floor-tabs">
        <button
          v-for="floor in floors"
          :key="floor"
          :class="['floor-btn', { active: selectedFloor === floor }]"
          @click="selectFloor(floor)"
        >
          {{ floor }} 楼
        </button>
      </div>
      <div class="stats">
        <span class="stat-item">
          <span class="label">总车位:</span>
          <span class="value">{{ totalSpaces }}</span>
        </span>
        <span class="stat-item">
          <span class="label">已占用:</span>
          <span class="value occupied">{{ occupiedCount }}</span>
        </span>
        <span class="stat-item">
          <span class="label">空闲:</span>
          <span class="value free">{{ freeCount }}</span>
        </span>
        <span class="stat-item debug">
          <span class="label">[调试]</span>
          <span class="value">{{ loading ? '加载中...' : (error ? '❌ 错误' : '✓ 已加载') }}</span>
        </span>
      </div>
    </div>

    <!-- SVG 地图容器 -->
    <div class="map-container">
      <svg
        v-if="svgContent"
        :viewBox="`0 0 1098 771`"
        class="parking-map"
        @click="handleMapClick"
        xmlns="http://www.w3.org/2000/svg"
        xmlns:xlink="http://www.w3.org/1999/xlink"
      >
        <!-- 动态插入 SVG 内容 - 使用 innerHTML 替代 v-html -->
        <g class="svg-content" ref="svgContentRef"></g>
        
        <!-- 停车位覆盖层 -->
        <g class="parking-overlay">
          <circle
            v-for="space in currentFloorSpaces"
            :key="space.space_id"
            :cx="space.center_x"
            :cy="space.center_y"
            r="25"
            :class="['space-marker', `status-${space.status}`]"
            :data-space-id="space.space_id"
            @click.stop="selectSpace(space)"
            @mouseover="hoveredSpace = space.space_id"
            @mouseout="hoveredSpace = null"
          >
            <title>{{ space.space_id }} - {{ getStatusLabel(space.status) }}</title>
          </circle>

          <!-- 悬停提示 -->
          <g v-if="hoveredSpace" class="hover-label">
            <text
              v-for="(space, idx) in currentFloorSpaces.filter(s => s.space_id === hoveredSpace)"
              :key="idx"
              :x="space.center_x"
              :y="space.center_y - 40"
              class="space-label"
              text-anchor="middle"
            >
              {{ space.space_id }} {{ space.status === 'occupied' ? `(${space.current_plate})` : '(空闲)' }}
            </text>
          </g>
        </g>
      </svg>

      <!-- 加载指示器 -->
      <div v-if="loading" class="loading-indicator">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="error-message">
        <p>{{ error }}</p>
        <button @click="loadFloor">重试</button>
      </div>
    </div>

    <!-- 空间详情面板 -->
    <div v-if="selectedSpace" class="details-panel">
      <div class="panel-header">
        <h3>{{ selectedSpace.space_id }}</h3>
        <button class="close-btn" @click="selectedSpace = null">✕</button>
      </div>
      <div class="panel-content">
        <p><strong>状态:</strong> <span :class="['status-badge', selectedSpace.status]">{{ getStatusLabel(selectedSpace.status) }}</span></p>
        <p v-if="selectedSpace.current_plate"><strong>车牌:</strong> {{ selectedSpace.current_plate }}</p>
        <p><strong>位置:</strong> X: {{ selectedSpace.x }}, Y: {{ selectedSpace.y }}</p>
        <p><strong>中心:</strong> X: {{ selectedSpace.center_x }}, Y: {{ selectedSpace.center_y }}</p>

        <!-- 绑定操作 -->
        <div v-if="selectedSpace.status === 'free'" class="actions">
          <button class="btn-bind" @click="openBindDialog">
            📱 绑定车牌
          </button>
        </div>

        <!-- 解绑操作 -->
        <div v-else class="actions">
          <button class="btn-clear" @click="clearBinding">
            🔓 解除绑定
          </button>
        </div>
      </div>
    </div>

    <!-- 绑定对话框 -->
    <div v-if="showBindDialog" class="modal-overlay" @click.self="showBindDialog = false">
      <div class="modal-dialog">
        <div class="modal-header">
          <h3>绑定车牌到 {{ selectedSpace?.space_id }}</h3>
          <button class="close-btn" @click="showBindDialog = false">✕</button>
        </div>
        <div class="modal-body">
          <input
            v-model="bindPlateNumber"
            type="text"
            placeholder="输入车牌号，如 京A88888"
            class="input-plate"
            @keyup.enter="submitBinding"
          />
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showBindDialog = false">取消</button>
          <button class="btn-submit" @click="submitBinding" :disabled="!bindPlateNumber">
            {{ bindingLoading ? '提交中...' : '确认绑定' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 寻车对话框 -->
    <div v-if="showFindDialog" class="modal-overlay" @click.self="showFindDialog = false">
      <div class="modal-dialog modal-find">
        <div class="modal-header">
          <h3>🔍 寻找我的车</h3>
          <button class="close-btn" @click="showFindDialog = false">✕</button>
        </div>
        <div class="modal-body">
          <input
            v-model="findPlateNumber"
            type="text"
            placeholder="输入车牌号"
            class="input-plate"
            @keyup.enter="submitFind"
          />
          <div v-if="findResult" :class="['find-result', findResult.status]">
            <p v-if="findResult.status === 'success'">
              <strong>✅ 找到您的车！</strong>
            </p>
            <p v-else>
              <strong>❌ 未找到您的车</strong>
            </p>
            <p v-if="findResult.data">车位: {{ findResult.data.space_id }}</p>
            <p v-if="findResult.data">楼层: {{ findResult.data.floor }}</p>
            <p v-if="findResult.error">错误: {{ findResult.error }}</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showFindDialog = false">关闭</button>
          <button class="btn-submit" @click="submitFind" :disabled="!findPlateNumber">
            {{ findLoading ? '搜索中...' : '搜索' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { getSpacesByFloor, bindPlate, findCarByPlate } from '@/api/parking.js'

// 状态
const floors = ref(['B2', 'B1', '1F'])
const selectedFloor = ref('B2')
const spaces = ref({})
const svgContent = ref('')
const svgContentRef = ref(null)
const loading = ref(false)
const error = ref(null)
const hoveredSpace = ref(null)
const selectedSpace = ref(null)
const showBindDialog = ref(false)
const showFindDialog = ref(false)
const bindPlateNumber = ref('')
const findPlateNumber = ref('')
const bindingLoading = ref(false)
const findLoading = ref(false)
const findResult = ref(null)

// 计算属性
const currentFloorSpaces = computed(() => {
  return spaces.value[selectedFloor.value] || []
})

const totalSpaces = computed(() => currentFloorSpaces.value.length)

const occupiedCount = computed(() => {
  return currentFloorSpaces.value.filter(s => s.status === 'occupied').length
})

const freeCount = computed(() => {
  return currentFloorSpaces.value.filter(s => s.status === 'free').length
})

// 方法
const selectFloor = async (floor) => {
  selectedFloor.value = floor
  selectedSpace.value = null
  await loadFloor()
}

const loadFloor = async () => {
  loading.value = true
  error.value = null
  
  console.log(`\n[LOAD_FLOOR] Starting to load floor: ${selectedFloor.value}`)
  
  try {
    console.log(`[LOAD_FLOOR] Calling getSpacesByFloor with floor=${selectedFloor.value}`)
    const response = await getSpacesByFloor(selectedFloor.value)
    console.log(`[LOAD_FLOOR] Full response:`, response)
    
    // 响应格式: { code: 200, floor: 'B2', data: [...], count: 65 }
    const data = response.data || []
    console.log(`[LOAD_FLOOR] Extracted data: type=${typeof data}, length=${Array.isArray(data) ? data.length : 'N/A'}`)
    console.log(`[LOAD_FLOOR] First 3 items:`, data.slice(0, 3))
    
    spaces.value[selectedFloor.value] = data
    console.log(`[LOAD_FLOOR] Assigned to spaces.value['${selectedFloor.value}']`)
    console.log(`[LOAD_FLOOR] Current floor spaces count: ${currentFloorSpaces.value.length}`)
    console.log(`[LOAD_FLOOR] All spaces keys:`, Object.keys(spaces.value))
  } catch (err) {
    error.value = '加载停车位数据失败: ' + err.message
    console.error('[LOAD_FLOOR] Error:', err)
  } finally {
    loading.value = false
    console.log(`[LOAD_FLOOR] Finished. loading=${loading.value}, error=${error.value}\n`)
  }
}

const loadSVG = async () => {
  try {
    console.log('[loadSVG] Fetching SVG from API...')
    const response = await fetch('/api/v1/parking/map/svg/')
    const result = await response.json()
    
    if (result.code === 200 && result.data?.svg) {
      svgContent.value = 'loaded'  // 标记为已加载，触发 SVG 元素渲染
      console.log('[loadSVG] SVG loaded, length:', result.data.svg.length)
      
      // 等待 DOM 更新后注入内容
      setTimeout(() => {
        if (svgContentRef.value) {
          svgContentRef.value.innerHTML = result.data.svg
          console.log('[loadSVG] SVG content injected successfully')
        } else {
          console.warn('[loadSVG] svgContentRef is not available')
        }
      }, 50)
    } else {
      console.warn('[loadSVG] Failed to load SVG:', result.error)
      svgContent.value = ''
    }
  } catch (err) {
    console.warn('[loadSVG] Error:', err)
    svgContent.value = ''
  }
}

const getStatusLabel = (status) => {
  return status === 'occupied' ? '已占用' : '空闲'
}

const selectSpace = (space) => {
  selectedSpace.value = space
}

const openBindDialog = () => {
  bindPlateNumber.value = ''
  showBindDialog.value = true
}

const submitBinding = async () => {
  if (!bindPlateNumber.value || !selectedSpace.value) return
  
  bindingLoading.value = true
  
  try {
    await bindPlate(selectedSpace.value.space_id, bindPlateNumber.value)
    
    // 更新本地数据
    const spaceIndex = currentFloorSpaces.value.findIndex(
      s => s.space_id === selectedSpace.value.space_id
    )
    if (spaceIndex !== -1) {
      currentFloorSpaces.value[spaceIndex].status = 'occupied'
      currentFloorSpaces.value[spaceIndex].current_plate = bindPlateNumber.value
    }
    
    showBindDialog.value = false
    selectedSpace.value = null
    alert('✅ 车牌绑定成功！')
  } catch (err) {
    alert('❌ 绑定失败: ' + err.message)
  } finally {
    bindingLoading.value = false
  }
}

const clearBinding = async () => {
  if (!selectedSpace.value) return
  
  if (!confirm(`确定要解除 ${selectedSpace.value.space_id} 的绑定吗？`)) {
    return
  }
  
  bindingLoading.value = true
  
  try {
    // 调用清除接口 (这里简化处理，实际应该有专门的 API)
    await bindPlate(selectedSpace.value.space_id, '')
    
    // 更新本地数据
    const spaceIndex = currentFloorSpaces.value.findIndex(
      s => s.space_id === selectedSpace.value.space_id
    )
    if (spaceIndex !== -1) {
      currentFloorSpaces.value[spaceIndex].status = 'free'
      currentFloorSpaces.value[spaceIndex].current_plate = null
    }
    
    selectedSpace.value = null
    alert('✅ 绑定已解除！')
  } catch (err) {
    alert('❌ 解除失败: ' + err.message)
  } finally {
    bindingLoading.value = false
  }
}

const submitFind = async () => {
  if (!findPlateNumber.value) return
  
  findLoading.value = true
  findResult.value = null
  
  try {
    const response = await findCarByPlate(findPlateNumber.value, selectedFloor.value)
    findResult.value = {
      status: 'success',
      data: response.data
    }
  } catch (err) {
    findResult.value = {
      status: 'error',
      error: err.message || '未找到该车辆'
    }
  } finally {
    findLoading.value = false
  }
}

const handleMapClick = (event) => {
  // 用于调试，可以查看点击位置
  const svg = event.currentTarget
  const rect = svg.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  console.log(`Clicked at SVG coordinates: ${x}, ${y}`)
}

// 生命周期
onMounted(async () => {
  console.log('[onMounted] Starting initialization...')
  await loadSVG()
  await loadFloor()
})

// 监听楼层变化，每 5 秒刷新一次数据
const pollInterval = setInterval(() => {
  if (!loading.value && !error.value) {
    loadFloor()
  }
}, 5000)

// 组件卸载时清理定时器
const cleanup = () => {
  clearInterval(pollInterval)
}

watch(() => selectedFloor.value, () => {
  cleanup()
})
</script>

<style scoped>
.multi-floor-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 16px;
  padding: 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 12px;
}

.floor-selector {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.floor-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.floor-btn {
  padding: 10px 16px;
  border: 2px solid #e0e0e0;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.floor-btn:hover {
  border-color: #2196F3;
  color: #2196F3;
}

.floor-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.stats {
  display: flex;
  gap: 24px;
  font-size: 14px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.stat-item.debug {
  background: #f0f0f0;
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.stat-item .label {
  font-weight: 600;
  color: #666;
}

.stat-item .value {
  font-weight: bold;
  font-size: 16px;
  color: #333;
}

.stat-item .value.occupied {
  color: #f44336;
}

.stat-item .value.free {
  color: #4caf50;
}

.map-container {
  flex: 1;
  position: relative;
  background: white;
  border-radius: 8px;
  overflow: auto;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.parking-map {
  width: 100%;
  height: 100%;
  max-width: 900px;
  cursor: pointer;
}

.space-marker {
  opacity: 0.7;
  transition: all 0.2s;
  cursor: pointer;
  stroke: white;
  stroke-width: 2;
}

.space-marker:hover {
  opacity: 1;
  stroke-width: 3;
  filter: drop-shadow(0 0 8px rgba(0, 0, 0, 0.3));
}

.space-marker.status-occupied {
  fill: #ffcdd2;
}

.space-marker.status-free {
  fill: #c8e6c9;
}

.hover-label {
  pointer-events: none;
}

.space-label {
  font-size: 12px;
  font-weight: bold;
  fill: #333;
  text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8);
}

.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e0e0e0;
  border-top-color: #2196F3;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  text-align: center;
  padding: 24px;
  color: #d32f2f;
}

.error-message button {
  margin-top: 12px;
  padding: 8px 16px;
  background: #d32f2f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.details-panel {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  max-width: 300px;
  margin-left: auto;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px 8px 0 0;
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

.panel-content {
  padding: 16px;
}

.panel-content p {
  margin: 8px 0;
  font-size: 14px;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.status-badge.occupied {
  background: #ffcdd2;
  color: #c62828;
}

.status-badge.free {
  background: #c8e6c9;
  color: #2e7d32;
}

.actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.btn-bind,
.btn-clear {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-bind {
  background: #4caf50;
  color: white;
}

.btn-bind:hover {
  background: #45a049;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.btn-clear {
  background: #ff9800;
  color: white;
}

.btn-clear:hover {
  background: #e68900;
  box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3);
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-dialog {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  max-width: 400px;
  width: 90%;
  max-height: 80vh;
  overflow: auto;
}

.modal-find {
  max-width: 500px;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px 12px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.modal-body {
  padding: 20px;
}

.input-plate {
  width: 100%;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.input-plate:focus {
  outline: none;
  border-color: #2196F3;
}

.find-result {
  margin-top: 16px;
  padding: 12px;
  border-radius: 6px;
  font-size: 14px;
}

.find-result.success {
  background: #c8e6c9;
  border: 1px solid #4caf50;
  color: #2e7d32;
}

.find-result.error {
  background: #ffcdd2;
  border: 1px solid #f44336;
  color: #c62828;
}

.modal-footer {
  padding: 16px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.btn-cancel,
.btn-submit {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-cancel {
  background: #e0e0e0;
  color: #333;
}

.btn-cancel:hover {
  background: #d0d0d0;
}

.btn-submit {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-submit:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transform: translateY(-2px);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
