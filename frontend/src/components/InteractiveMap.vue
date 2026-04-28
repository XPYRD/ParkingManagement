<template>
  <div class="interactive-map-container">
    <!-- 顶部控制栏 -->
    <div class="map-header">
      <h2>🅿️ 室内停车场地图</h2>
      <div class="header-controls">
        <el-input
          v-model="searchPlate"
          placeholder="输入车牌号查询..."
          class="search-input"
          clearable
          @keyup.enter="handleFindCar"
        >
          <template #suffix>
            <el-icon class="is-loading">
              <search />
            </el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="handleFindCar" :loading="findingCar">
          寻车
        </el-button>
        <el-button @click="handleRefresh" :loading="loading">
          刷新
        </el-button>
      </div>
    </div>

    <!-- SVG 地图容器 -->
    <div class="map-viewer" ref="mapContainer">
      <svg
        v-if="svgContent"
        :viewBox="svgViewBox"
        class="parking-map-svg"
        @click="handleSvgClick"
      >
        <!-- 动态加载SVG内容 -->
        <g v-html="svgContent"></g>

        <!-- 路径规划结果（动态绘制） -->
        <g v-if="pathData" class="path-layer">
          <polyline
            :points="pathData.points"
            class="path-line"
            stroke="blue"
            stroke-width="3"
            fill="none"
            stroke-dasharray="5,5"
          />
          <!-- 箭头标记 -->
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 10 3, 0 6" fill="blue" />
            </marker>
          </defs>
          <polyline
            :points="pathData.points"
            class="path-arrow"
            stroke="blue"
            stroke-width="2"
            fill="none"
            marker-end="url(#arrowhead)"
            stroke-dasharray="5,5"
          />
        </g>
      </svg>
      <div v-else class="map-loading">
        <el-spin size="large" description="加载地图中..." />
      </div>
    </div>

    <!-- 右侧信息面板 -->
    <div class="info-sidebar">
      <div class="sidebar-header">
        <h3>🔍 实时状态</h3>
        <el-tag :type="statusSummary.type" effect="dark">
          空闲: {{ statusSummary.free }} | 占用: {{ statusSummary.occupied }} | 预约: {{ statusSummary.reserved }}
        </el-tag>
      </div>

      <!-- 选中车位信息 -->
      <div v-if="selectedSpace" class="space-info">
        <el-divider>选中车位</el-divider>
        <div class="info-item">
          <span class="label">车位编号:</span>
          <span class="value">{{ selectedSpace.space_id }}</span>
        </div>
        <div class="info-item">
          <span class="label">状态:</span>
          <el-tag :type="getStatusTagType(selectedSpace.status)">
            {{ getStatusText(selectedSpace.status) }}
          </el-tag>
        </div>
        <div v-if="selectedSpace.current_plate" class="info-item">
          <span class="label">车牌号:</span>
          <span class="value">{{ selectedSpace.current_plate }}</span>
        </div>
        <div class="info-item">
          <span class="label">更新时间:</span>
          <span class="value">{{ formatTime(selectedSpace.last_updated) }}</span>
        </div>

        <!-- 绑定按钮（仅当车位占用时） -->
        <el-button
          v-if="selectedSpace.status === 'occupied' && !selectedSpace.current_plate"
          type="primary"
          @click="handleBindPlate"
          class="bind-btn"
        >
          📱 扫码绑定车牌
        </el-button>
      </div>

      <!-- 寻车结果 -->
      <div v-if="findCarResult" class="find-car-result">
        <el-divider>寻车结果</el-divider>
        <div class="info-item">
          <span class="label">车牌号:</span>
          <span class="value">{{ findCarResult.plate_number }}</span>
        </div>
        <div class="info-item">
          <span class="label">车位:</span>
          <span class="value">{{ findCarResult.space_id }}</span>
        </div>
        <div class="info-item">
          <span class="label">位置:</span>
          <span class="value">{{ findCarResult.location_desc }}</span>
        </div>
        <el-button type="info" @click="findCarResult = null">
          清除结果
        </el-button>
      </div>

      <!-- 最近操作日志 -->
      <div class="operation-log">
        <el-divider>操作日志</el-divider>
        <div class="log-content">
          <div v-for="(log, index) in operationLogs.slice(-5)" :key="index" class="log-item">
            <span class="log-time">{{ formatTime(log.time) }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 绑定车牌弹窗 -->
    <el-dialog v-model="bindDialogVisible" title="📱 绑定车牌" width="40%">
      <div class="bind-dialog">
        <div class="qr-display">
          <p>🔲 二维码令牌</p>
          <code>{{ selectedSpace?.qr_code_token }}</code>
        </div>

        <el-form :model="bindForm" @submit.prevent="submitBind">
          <el-form-item label="车牌号" required>
            <el-input
              v-model="bindForm.plate_number"
              placeholder="例: 京A88888"
              clearable
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="bindDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitBind" :loading="bindingLoading">
            确认绑定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import axios from 'axios'

// ============ 响应式状态 ============
const loading = ref(false)
const findingCar = ref(false)
const bindingLoading = ref(false)
const svgContent = ref('')
const svgViewBox = ref('0 0 1200 800')
const searchPlate = ref('')
const selectedSpace = ref(null)
const findCarResult = ref(null)
const pathData = ref(null)
const operationLogs = ref([])
const bindDialogVisible = ref(false)
const bindForm = ref({
  plate_number: ''
})

// 所有车位数据
const spacesMap = ref(new Map())
const mapContainer = ref(null)

// ============ 计算属性 ============
const statusSummary = computed(() => {
  let free = 0
  let occupied = 0
  let reserved = 0
  spacesMap.value.forEach(space => {
    if (space.status === 'free') free++
    else if (space.status === 'occupied') occupied++
    else if (space.status === 'reserved') reserved++
  })
  return {
    free,
    occupied,
    reserved,
    type: free > 0 ? 'success' : 'warning'
  }
})

function getStatusTagType(status) {
  if (status === 'free') return 'success'
  if (status === 'reserved') return 'warning'
  if (status === 'maintenance') return 'info'
  return 'danger'
}

function getStatusText(status) {
  if (status === 'free') return '🟢 空闲'
  if (status === 'reserved') return '🟡 已预约'
  if (status === 'maintenance') return '⚪ 维修中'
  return '🔴 占用'
}

// ============ 方法 ============

/**
 * 从SVG ID获取对应的车位数据
 */
function getSpaceFromSvgId(svgId) {
  const spaceId = svgId.replace('space-', 'space_')
  return spacesMap.value.get(spaceId)
}

/**
 * 加载SVG地图
 */
async function loadSvgMap() {
  try {
    // 这里可以从服务器加载SVG或使用静态SVG
    // 示例：使用一个简单的停车场SVG模板
    const response = await axios.get('/src/assets/interactive_map.svg')
    svgContent.value = response.data
  } catch (error) {
    console.warn('SVG加载失败，使用默认网格布局')
    generateDefaultSvg()
  }
}

/**
 * 生成默认SVG（当没有真实SVG时）
 */
function generateDefaultSvg() {
  const svg = generateGridSvg(4, 6, 150, 100)
  svgContent.value = svg
}

/**
 * 生成网格形停车场SVG
 */
function generateGridSvg(rows, cols, width, height) {
  let svg = ''
  let spaceIndex = 1
  
  for (let i = 0; i < rows; i++) {
    for (let j = 0; j < cols; j++) {
      const x = j * (width + 20) + 50
      const y = i * (height + 20) + 50
      const spaceId = `space_A${String(spaceIndex).padStart(3, '0')}`
      
      svg += `
        <g class="parking-space" id="space-${spaceId}">
          <rect
            x="${x}" y="${y}"
            width="${width}" height="${height}"
            class="space-rect"
            fill="#e0f7fa"
            stroke="#0288d1"
            stroke-width="2"
            rx="4"
            data-space-id="${spaceId}"
          />
          <text
            x="${x + width / 2}" y="${y + height / 2}"
            text-anchor="middle"
            dominant-baseline="middle"
            class="space-label"
            font-size="14"
            font-weight="bold"
            fill="#01579b"
            pointer-events="none"
          >
            ${spaceIndex}
          </text>
        </g>
      `
      spaceIndex++
    }
  }
  
  return svg
}

/**
 * 轮询获取车位状态
 */
async function pollSpacesStatus() {
  try {
    loading.value = true
    const response = await axios.get('/api/v1/map/spaces/')
    
    if (response.data.code === 200) {
      const spaces = response.data.data
      
      // 更新车位状态并刷新UI
      spaces.forEach(space => {
        spacesMap.value.set(space.space_id, {
          space_id: space.space_id,
          status: space.status,
          is_damaged: Boolean(space.is_damaged),
          marker_color: space.marker_color || null,
          current_plate: space.current_plate,
          last_updated: new Date()
        })
        
        // 更新SVG颜色
        updateSpaceColor(space.space_id, space.status, space.marker_color)
      })
      
      addLog('车位状态已刷新')
    }
  } catch (error) {
    ElMessage.error('获取车位状态失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

/**
 * 更新SVG车位颜色
 */
function updateSpaceColor(spaceId, status, markerColor = null) {
  const svgId = `space-${spaceId}`
  const element = document.querySelector(`#${svgId} .space-rect`)
  
  if (element) {
    const colorMap = {
      free: '#e0f7fa',
      occupied: '#ffebee',
      reserved: '#fff7e6',
      maintenance: '#f3f4f6',
    }
    const strokeMap = {
      free: '#0288d1',
      occupied: '#d32f2f',
      reserved: '#f59e0b',
      maintenance: '#9ca3af',
    }
    const color = markerColor || colorMap[status] || '#ffffff'
    const stroke = strokeMap[status] || '#64748b'
    element.setAttribute('fill', color)
    element.setAttribute('stroke', stroke)
  }
}

/**
 * 处理SVG点击事件
 */
function handleSvgClick(event) {
  const target = event.target
  
  if (target.tagName === 'rect' && target.classList.contains('space-rect')) {
    const spaceId = target.getAttribute('data-space-id')
    selectedSpace.value = spacesMap.value.get(spaceId) || {
      space_id: spaceId,
      status: 'unknown',
      current_plate: null,
      last_updated: new Date()
    }
    
    // 高亮选中的车位
    highlightSpace(spaceId)
    addLog(`选中车位: ${spaceId}`)
  }
}

/**
 * 高亮选中的车位
 */
function highlightSpace(spaceId) {
  // 移除所有高亮
  document.querySelectorAll('.space-rect').forEach(el => {
    el.style.stroke = el.getAttribute('fill') === '#e0f7fa' ? '#0288d1' : '#d32f2f'
    el.style.strokeWidth = '2'
  })
  
  // 高亮当前车位
  const svgId = `space-${spaceId}`
  const element = document.querySelector(`#${svgId} .space-rect`)
  if (element) {
    element.style.stroke = '#1976d2'
    element.style.strokeWidth = '3'
  }
}

/**
 * 寻车处理
 */
async function handleFindCar() {
  const plate = searchPlate.value.trim()
  if (!plate) {
    ElMessage.warning('请输入车牌号')
    return
  }
  
  try {
    findingCar.value = true
    const response = await axios.get('/api/v1/map/find_car/', {
      params: { plate_number: plate }
    })
    
    if (response.data.code === 200) {
      findCarResult.value = response.data.data
      addLog(`找到车牌 ${plate} 在 ${response.data.data.space_id}`)
      
      // 高亮该车位
      highlightSpace(response.data.data.space_id)
      ElNotification.success({
        title: '✅ 寻车成功',
        message: `车牌 ${plate} 位于 ${response.data.data.location_desc}`,
        duration: 5000
      })
    } else {
      ElMessage.error(response.data.error || '未找到该车')
    }
  } catch (error) {
    ElMessage.error('寻车失败: ' + (error.response?.data?.error || error.message))
    addLog(`寻车失败: ${error.message}`, 'error')
  } finally {
    findingCar.value = false
  }
}

/**
 * 刷新地图
 */
async function handleRefresh() {
  await pollSpacesStatus()
}

/**
 * 处理绑定车牌
 */
function handleBindPlate() {
  if (!selectedSpace.value) return
  bindDialogVisible.value = true
  bindForm.value.plate_number = ''
}

/**
 * 提交绑定
 */
async function submitBind() {
  const plate = bindForm.value.plate_number.trim()
  if (!plate) {
    ElMessage.warning('请输入车牌号')
    return
  }
  
  if (!selectedSpace.value) return
  
  try {
    bindingLoading.value = true
    const response = await axios.post('/api/v1/parking_spaces/bind/', {
      qr_code_token: selectedSpace.value.qr_code_token,
      plate_number: plate
    })
    
    if (response.data.code === 200) {
      ElMessage.success('✅ 绑定成功！')
      addLog(`车牌 ${plate} 已绑定到 ${selectedSpace.value.space_id}`)
      
      // 更新本地数据
      selectedSpace.value.current_plate = plate
      spacesMap.value.get(selectedSpace.value.space_id).current_plate = plate
      
      bindDialogVisible.value = false
      bindForm.value.plate_number = ''
    } else {
      ElMessage.error(response.data.error || '绑定失败')
    }
  } catch (error) {
    ElMessage.error('绑定失败: ' + (error.response?.data?.error || error.message))
  } finally {
    bindingLoading.value = false
  }
}

/**
 * 添加操作日志
 */
function addLog(message, type = 'info') {
  operationLogs.value.push({
    message,
    type,
    time: new Date()
  })
}

/**
 * 格式化时间
 */
function formatTime(date) {
  if (!date) return '-'
  const d = new Date(date)
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  return `${hours}:${minutes}:${seconds}`
}

// ============ 生命周期 ============
onMounted(async () => {
  // 加载SVG地图
  await loadSvgMap()
  
  // 初始化轮询
  await pollSpacesStatus()
  
  // 启动定时刷新（每5秒）
  setInterval(() => {
    pollSpacesStatus()
  }, 5000)
})
</script>

<style scoped lang="scss">
.interactive-map-container {
  display: flex;
  height: 100vh;
  background-color: #f5f7fa;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;

  .map-header {
    position: absolute;
    top: 0;
    left: 0;
    right: 200px;
    height: 70px;
    background: white;
    padding: 15px 20px;
    border-bottom: 1px solid #dcdfe6;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    z-index: 100;

    h2 {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
      color: #303133;
    }

    .header-controls {
      display: flex;
      gap: 10px;
      align-items: center;

      .search-input {
        width: 250px;
      }
    }
  }

  .map-viewer {
    flex: 1;
    margin-top: 70px;
    margin-right: 200px;
    overflow: auto;
    background: linear-gradient(135deg, #f5f7fa 0%, #e8eaef 100%);
    position: relative;

    .parking-map-svg {
      width: 100%;
      height: 100%;
      display: block;
      padding: 20px;

      .space-rect {
        cursor: pointer;
        transition: all 0.3s ease;

        &:hover {
          filter: brightness(0.9);
          stroke-width: 3;
        }
      }

      .space-label {
        pointer-events: none;
        user-select: none;
      }

      .path-layer {
        .path-line,
        .path-arrow {
          animation: dash 20s linear infinite;
        }
      }
    }

    .map-loading {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100%;
    }
  }

  .info-sidebar {
    width: 200px;
    background: white;
    border-left: 1px solid #dcdfe6;
    overflow-y: auto;
    padding: 15px;
    margin-top: 70px;

    .sidebar-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 15px;

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }
    }

    .space-info,
    .find-car-result {
      margin-bottom: 20px;
      padding: 15px;
      background-color: #f5f7fa;
      border-radius: 4px;

      .info-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
        font-size: 12px;

        .label {
          font-weight: 600;
          color: #606266;
        }

        .value {
          color: #909399;
          word-break: break-all;
        }
      }

      .bind-btn {
        width: 100%;
        margin-top: 10px;
      }
    }

    .operation-log {
      margin-top: 20px;

      .log-content {
        max-height: 200px;
        overflow-y: auto;
        background-color: #fafafa;
        border-radius: 4px;
        padding: 10px;

        .log-item {
          display: flex;
          gap: 10px;
          margin-bottom: 8px;
          font-size: 11px;
          line-height: 1.4;

          .log-time {
            color: #909399;
            flex-shrink: 0;
            font-family: monospace;
          }

          .log-message {
            color: #606266;
            flex: 1;
            word-break: break-all;
          }
        }
      }
    }
  }
}

.bind-dialog {
  .qr-display {
    text-align: center;
    margin-bottom: 20px;

    p {
      font-size: 12px;
      color: #909399;
      margin-bottom: 8px;
    }

    code {
      display: block;
      padding: 10px;
      background-color: #f5f7fa;
      border-radius: 4px;
      font-family: monospace;
      font-size: 12px;
      color: #303133;
      word-break: break-all;
    }
  }
}

@keyframes dash {
  to {
    stroke-dashoffset: -20;
  }
}
</style>
